import json

from langchain.tools import ToolRuntime, tool
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from pydantic import ValidationError

from app.core.state import RequirementPatch, TravelState
from app.core.transitions import ConfirmationContext, requirement_update, confirmation_update


def tool_result(update: dict, text: str, tool_call_id: str) -> Command:
    return Command(update={**update, "messages": [ToolMessage(content=text, tool_call_id=tool_call_id)]})


@tool
def record_requirement_tool(
    updates: RequirementPatch, runtime: ToolRuntime[ConfirmationContext, TravelState]
) -> Command:
    """记录用户明确提供的新需求，信息不全也可保存，只填已知字段。

    修改目的地、日期、人数等有效需求将撤销旧确认、清空下游并要求重新确认。
    未提及字段省略，不猜测；预算单位元/人；日期 YYYY-MM-DD。
    """
    try:
        update = requirement_update(runtime.state, updates)
    except ValidationError:
        return tool_result({}, "需求未保存：预算上下限冲突或字段格式不合法，请向用户澄清。", runtime.tool_call_id)
    current = {**runtime.state, **update}
    result = {key: current.get(key) for key in (
        "user_requirement", "requirement_revision", "missing_fields", "requirement_ready",
        "requirement_confirmed", "current_step",
    )}
    result["changed"] = bool(update)
    return tool_result(update, json.dumps(result, ensure_ascii=False), runtime.tool_call_id)


@tool
def confirm_requirement_tool(runtime: ToolRuntime[ConfirmationContext, TravelState]) -> Command:
    """确认完整的当前需求并进入交通规划。只能在本轮用户独立回复“确认”时使用。

    后端会核对用户授权、必填字段及需求版本。不能代用户确认，不能在同轮改需求后确认。
    """
    try:
        update = confirmation_update(runtime.state, runtime.context or ConfirmationContext())
    except ValueError as exc:
        return tool_result({}, str(exc), runtime.tool_call_id)
    return tool_result(update, "当前需求已确认，进入交通规划；查询必须使用当前可用工具，不得编造班次或票价。", runtime.tool_call_id)
