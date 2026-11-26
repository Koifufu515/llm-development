"""不依赖模型的业务规则：修改撤销确认；确认绑定需求版本。"""
from dataclasses import dataclass

from app.core.state import RequirementPatch, merge_requirement, missing_fields


@dataclass(frozen=True)
class ConfirmationContext:
    approved_revision: int | None = None


def confirmation_context(message: str, revision: int) -> ConfirmationContext:
    normalized = message.strip().rstrip("。.!！ ")
    # 明确而窄的快捷确认；混有修改、否定或疑问的消息交给模型理解，不授予确认权限。
    standalone = {"确认", "确认无误", "确认继续", "确认，继续", "确认,继续", "就按这个来", "按这个来"}
    return ConfirmationContext(revision if normalized in standalone else None)


def requirement_update(state: dict, patch: RequirementPatch, force: bool = False) -> dict:
    old = state.get("user_requirement", {})
    requirement = merge_requirement(old, patch)
    if requirement == old and not force:
        return {}
    missing = missing_fields(requirement)
    # 首个版本采用保守依赖规则：任何有效需求修改都使下游结果过期。
    return {
        "user_requirement": requirement,
        "requirement_revision": state.get("requirement_revision", 0) + 1,
        "missing_fields": missing,
        "requirement_ready": not missing,
        "requirement_confirmed": False,
        "confirmed_revision": None,
        "current_step": "requirement_collection",
        "selected_destination": None,
        "transport_options": [], "last_transport_query": None, "selected_transport": None,
        "accommodation_options": [], "selected_accommodation_types": [],
        "food_options": [], "selected_food_types": [],
        "itinerary": None, "budget": None, "report": None, "planning_result": None, "planning_stops": [],
    }


def confirmation_update(state: dict, context: ConfirmationContext) -> dict:
    if missing_fields(state.get("user_requirement", {})):
        raise ValueError("需求不完整，请先补齐信息，不能推进")
    if context.approved_revision is None:
        raise ValueError("用户尚未明确确认，请让用户单独回复“确认”")
    revision = state.get("requirement_revision", 0)
    if context.approved_revision != revision:
        raise ValueError("需求已变更，旧确认无效，请重新确认最新需求")
    if state.get("requirement_confirmed") and state.get("confirmed_revision") == revision:
        return {}  # 重复确认幂等，不向后跳步。
    if state.get("current_step", "requirement_collection") != "requirement_collection":
        raise ValueError("当前步骤不允许确认需求")
    return {
        "requirement_confirmed": True,
        "confirmed_revision": revision,
        "selected_destination": state["user_requirement"]["destination"],
        "current_step": "transport_planning",
    }
