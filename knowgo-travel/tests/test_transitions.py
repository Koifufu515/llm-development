from types import SimpleNamespace

import pytest

from app.core.state import RequirementPatch
from app.core.transitions import ConfirmationContext, confirmation_context, requirement_update, confirmation_update

FULL = {"departure_city": "上海", "destination": "杭州", "departure_date": "2026-11-15", "travel_days": 3, "adult_count": 1, "children_count": 0, "budget_max": 2000}


def ready(**extra):
    return {"user_requirement": dict(FULL), "requirement_revision": 1, "current_step": "requirement_collection", **extra}


def test_missing_information_cannot_be_confirmed():
    with pytest.raises(ValueError, match="不完整"):
        confirmation_update({"user_requirement": {"destination": "杭州"}}, ConfirmationContext(0))


def test_model_cannot_confirm_without_user_authorization():
    with pytest.raises(ValueError, match="明确确认"):
        confirmation_update(ready(), ConfirmationContext())


def test_user_confirmation_advances_known_destination_to_transport():
    result = confirmation_update(ready(), ConfirmationContext(1))
    assert result["current_step"] == "transport_planning"
    assert result["requirement_confirmed"] is True
    assert result["confirmed_revision"] == 1
    assert result["selected_destination"] == "杭州"


def test_stale_confirmation_does_not_approve_changed_requirement():
    with pytest.raises(ValueError, match="已变更"):
        confirmation_update(ready(requirement_revision=2), ConfirmationContext(1))


def test_destination_change_clears_downstream_and_preserves_common_fields():
    before = ready(requirement_confirmed=True, confirmed_revision=1, current_step="itinerary_generation",
                   selected_destination="杭州", transport_options=[{"city": "杭州"}], selected_transport="train",
                   accommodation_options=[{"city": "杭州"}], itinerary=[{"city": "杭州"}], budget={"total": 1000})
    result = requirement_update(before, RequirementPatch(destination="苏州"))
    assert result["user_requirement"] == {**FULL, "destination": "苏州"}
    assert result["requirement_revision"] == 2
    assert result["requirement_confirmed"] is False
    assert result["confirmed_revision"] is None
    assert result["current_step"] == "requirement_collection"
    assert result["transport_options"] == []
    assert result["selected_transport"] is None
    assert result["accommodation_options"] == []
    assert result["itinerary"] is None
    assert result["budget"] is None


def test_unchanged_record_does_not_cancel_confirmation():
    result = requirement_update(ready(requirement_confirmed=True, confirmed_revision=1, current_step="transport_planning"), RequirementPatch(destination="杭州"))
    assert result == {}


@pytest.mark.parametrize("message", ["确认，同时改成苏州", "不要确认", "解释一下确认是什么意思"])
def test_only_explicit_standalone_confirmation_is_authorized(message):
    assert confirmation_context(message, 1).approved_revision is None


def test_standalone_confirmation_uses_server_revision():
    assert confirmation_context("确认！", 2).approved_revision == 2


def test_step_middleware_hides_confirmation_until_ready_and_authorized():
    from app.core.middleware import allowed_tool_names
    assert "confirm_requirement_tool" not in allowed_tool_names(ready(), ConfirmationContext())
    assert "confirm_requirement_tool" in allowed_tool_names(ready(), ConfirmationContext(1))
    assert "confirm_requirement_tool" not in allowed_tool_names(ready(requirement_confirmed=True), ConfirmationContext(1))
    assert "confirm_requirement_tool" not in allowed_tool_names({"user_requirement": {}}, ConfirmationContext(0))


def test_repeat_confirmation_is_idempotent():
    state = ready(requirement_confirmed=True, confirmed_revision=1, current_step="transport_planning")
    assert confirmation_update(state, ConfirmationContext(1)) == {}
