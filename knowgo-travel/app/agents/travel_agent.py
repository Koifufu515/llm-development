from datetime import datetime
from zoneinfo import ZoneInfo

from langchain.agents import create_agent

from app.core.state import TravelState
from app.tools.state_transition import record_requirement_tool, confirm_requirement_tool
from app.core.transitions import ConfirmationContext
from app.core.middleware import StepConfigMiddleware


def create_travel_agent(model, checkpointer, extra_tools=None, memory=None):
    today = datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat()
    prompt = f"""你是知行旅行助手，负责需求收集、确认与交通规划入口。今天是中国时间 {today}。
用户提供任何已知旅行字段时，先调用 record_requirement_tool 保存，再根据工具结果回复。
只记录用户明确说明的信息；未提供的城市、日期、人数不可猜测。未知字段省略。
预算是元/人；如果用户没有说明总预算还是人均预算，先澄清，不擅自当成人均。
只有用户明确说“每人/人均”或确认过预算口径时，才写入 budget_min/budget_max。
“杭州三天”一般表示目的地杭州、天数3，不代表出发地杭州。
后续“从上海出发”只更新出发地，保持已保存的目的地/天数。一次问1～2个缺项。
相对日期按今天换算，模糊日期追问；过去日期需澄清，不推进。
必须包含出发地、目的地、日期、天数、成人数、儿童数（没有儿童要用户确认0）、每人预算上限。
字段齐全先总结并邀请用户单独回复“确认”；只有确认工具成功才算进入下一阶段。
高铁/动车查询以query_train_tickets返回为准；用户选择车次时调用select_transport，之后澄清每间房每晚住宿与每人每天餐饮预算，用finalize_plan生成行程。酒店航班服务缺少凭证时必须明确说明，不能虚构实时结果。用户明确要求记住偏好时调用remember_preferences。
不要反复保存相同字段形成循环。工具返回后用自然语言回复，不向用户输出工具原始JSON。
"""
    if memory:
        import json
        prompt += "\n已保存的用户偏好（作为参考，当前用户明确需求优先）：" + json.dumps(memory,ensure_ascii=False)
    return create_agent(
        model=model, tools=[record_requirement_tool, confirm_requirement_tool, *(extra_tools or [])], system_prompt=prompt,
        middleware=[StepConfigMiddleware()], context_schema=ConfirmationContext,
        state_schema=TravelState, checkpointer=checkpointer,
    )
