from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.core.state import RequirementPatch, merge_requirement, missing_fields
from app.tools.state_transition import record_requirement_tool


def test_followup_preserves_prior_requirement():
    initial = {"destination": "杭州", "travel_days": 3, "budget_max": 2000}
    actual = merge_requirement(initial, RequirementPatch(departure_city="上海"))
    assert actual == {**initial, "departure_city": "上海"}


def test_unknowns_do_not_overwrite_and_zero_children_is_known():
    result = merge_requirement({"destination": "杭州"}, RequirementPatch(destination=None, children_count=0))
    assert result == {"destination": "杭州", "children_count": 0}
    assert "children_count" not in missing_fields(result)


@pytest.mark.parametrize("invalid", [{"travel_days": 0}, {"budget_max": -1}, {"departure_date": "2026-02-30"}])
def test_reject_invalid_requirement(invalid):
    with pytest.raises(ValidationError):
        RequirementPatch(**invalid)


def test_budget_range_validated_after_merging_turns():
    runtime = SimpleNamespace(state={"user_requirement": {"budget_min": 1000, "budget_max": 2000}}, tool_call_id="test-call")
    result = record_requirement_tool.func(RequirementPatch(budget_max=500), runtime)
    assert "user_requirement" not in result.update
    assert "未保存" in result.update["messages"][0].content


def test_incomplete_requirement_does_not_advance():
    runtime = SimpleNamespace(state={}, tool_call_id="test-call")
    update = record_requirement_tool.func(RequirementPatch(destination="杭州", travel_days=3), runtime).update
    assert update["requirement_ready"] is False
    assert update["current_step"] == "requirement_collection"
    assert "departure_city" in update["missing_fields"]


def test_tool_runtime_is_not_exposed_to_model():
    assert list(record_requirement_tool.args) == ["updates"]
