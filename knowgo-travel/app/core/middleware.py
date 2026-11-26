"""每次模型调用前按最新状态注入步骤与工具；执行时再次检查。"""
import json
import re

from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from app.core.state import missing_fields


def allowed_tool_names(state: dict, context) -> set[str]:
    names = {"record_requirement_tool", "remember_preferences", "query_hotels", "query_flights", "query_driving"}
    if (not missing_fields(state.get("user_requirement", {}))
            and not state.get("requirement_confirmed", False)
            and context is not None
            and context.approved_revision == state.get("requirement_revision", 0)):
        names.add("confirm_requirement_tool")
    if state.get("requirement_confirmed") and state.get("current_step") == "transport_planning":
        names.update({"get_city_location", "get_weather_forecast", "query_train_tickets"})
    if state.get("requirement_confirmed") and state.get("current_step") == "transport_planning":
        names.add("select_transport")
    if state.get("requirement_confirmed") and state.get("current_step") == "accommodation_planning":
        names.add("finalize_plan")
    return names


class StepConfigMiddleware(AgentMiddleware):
    async def awrap_model_call(self, request, handler):
        names = allowed_tool_names(request.state, request.runtime.context)
        current = {key: request.state.get(key) for key in (
            "current_step", "user_requirement", "requirement_revision", "requirement_confirmed",
        )}
        guidance = """以下JSON是数据库中的当前状态，优先于历史对话中的旧需求。
收集阶段：有新增/修改先调用记录工具，完整后总结并请用户单独回复“确认”。
如果本轮可用工具含 confirm_requirement_tool 且用户说确认，必须调用它，不只口头说已确认。
确认成功后不要再记录相同字段或重复确认；仅告知进入交通规划。
交通阶段：若工具列表有 get_city_location，可查询城市省份/坐标；有 get_weather_forecast，可查询天气。
用户问天气必须实际调用天气工具，不可凭记忆回答。用户明确问“这几天/近期”时不传date；
问出行当天或未说明日期时，用 user_requirement.departure_date；未指定城市时用已确认目的地。
只有工具 status=ok 才能回答具体天气；status=unavailable 时说明原因。
date_out_of_range 必须说明请求日期超出工具返回的预报窗口，不能用其他日期的数据冒充。
回答要带天气来源、预报日期、查询时间；天气描述使用工具返回的 weather_description，数值为空时说明缺失，不猜测。天气查询不改变需求或推进步骤。
工具未加载或失败时明确说本次查不到，不要声称已查询成功。
查询交通或车票时调用query_train_tickets，以当前已确认行程为准。只查去程高铁/动车，不承诺已选定或已订票。
日期超出窗口、返回空数组、外部服务失败是不同结果，按工具消息说明，不自动改日期，不虚构车次/票价。
查询参数已由代码守卫，用户要换日期或城市时先记录并重新确认。班次表将由代码根据本轮工具结果渲染，模型不要重复写表格。
用户明确选择已展示的车次时调用select_transport，使用当前候选option_id，不得自行选择。住宿阶段先让用户给每间房每晚和每人每天餐饮估算，用户同意后调用finalize_plan。生成工具返回完整行程后可展示逐日安排和预算。酒店、航班和驾车查询分别使用query_hotels/query_flights/query_driving。只能按成功的实际返回说明，失败就说明失败；不得声称已预订。
交通阶段用户修改需求仍调用记录工具，修改后回到需求收集，重新总结并请用户确认。
一次只调用一个状态工具，等工具结果返回后再决定下一步。
"""
        base = request.system_message.content if request.system_message else ""
        prompt = f"{base}\n{guidance}\n当前状态JSON：{json.dumps(current, ensure_ascii=False)}"
        choice=request.tool_choice
        messages=request.state.get("messages",[])
        human_index=next((i for i in range(len(messages)-1,-1,-1) if isinstance(messages[i],HumanMessage)),None)
        if human_index is not None:
            explicit=bool(re.match(r"^(?:请)?(?:长期)?(?:记住|保存我的偏好|更新我的长期偏好)",str(messages[human_index].content).strip()))
            saved=any(isinstance(m,ToolMessage) and m.name=="remember_preferences" for m in messages[human_index+1:])
            if explicit and not saved and any(t.name=="remember_preferences" for t in request.tools):
                choice={"type":"function","function":{"name":"remember_preferences"}}
        return await handler(request.override(
            tool_choice=choice,
            system_message=SystemMessage(content=prompt),
            tools=[tool for tool in request.tools if tool.name in names],
        ))

    async def awrap_tool_call(self, request, handler):
        messages = request.state.get("messages", [])
        last_ai = next((m for m in reversed(messages) if isinstance(m, AIMessage)), None)
        if last_ai and len(last_ai.tool_calls) > 1:
            return ToolMessage(content="本轮拒绝并行状态变更，请一次调用一个工具。", tool_call_id=request.tool_call["id"])
        # 可见性是第一层；即使模型产生不可用的工具调用，执行层也会拦截。
        runtime = request.runtime
        if request.tool_call["name"] not in allowed_tool_names(request.state, runtime.context):
            return ToolMessage(content="当前状态或用户授权不允许执行该工具。", tool_call_id=request.tool_call["id"])
        return await handler(request)
