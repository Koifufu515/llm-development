"""按原教程保留 AgentState 和 user_requirement；本阶段允许逐轮补齐需求。"""
from datetime import date
from typing import Literal

from langchain.agents import AgentState
from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing_extensions import NotRequired

PlanningStep = Literal[
    "requirement_collection", "destination_recommendation", "transport_planning",
    "accommodation_planning", "food_planning", "itinerary_generation",
    "budget_summarization", "report_generation",
]


class RequirementPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    departure_city: str | None = Field(None, min_length=1, max_length=80)
    destination: str | None = Field(None, min_length=1, max_length=80)
    departure_date: date | None = None
    travel_days: int | None = Field(None, ge=1, le=60)
    adult_count: int | None = Field(None, ge=1, le=30)
    children_count: int | None = Field(None, ge=0, le=30)
    budget_min: float | None = Field(None, ge=0, allow_inf_nan=False)
    budget_max: float | None = Field(None, ge=0, allow_inf_nan=False)
    travel_styles: list[str] | None = Field(None, max_length=8)
    special_needs: str | None = Field(None, max_length=1000)

    @model_validator(mode="after")
    def valid_budget(self):
        if self.budget_min is not None and self.budget_max is not None:
            if self.budget_min > self.budget_max:
                raise ValueError("预算下限不能超过上限")
        return self


FIELD_LABELS = {
    "departure_city": "出发城市", "destination": "目的地", "departure_date": "出发日期",
    "travel_days": "出行天数", "adult_count": "成人数", "children_count": "儿童数",
    "budget_max": "每人预算上限",
}


def merge_requirement(current: dict, patch: RequirementPatch) -> dict:
    # 没提及的字段不会用 None 覆盖；撤销/清空操作在后续回退模块单独定义。
    merged = {**current, **patch.model_dump(mode="json", exclude_none=True)}
    return RequirementPatch.model_validate(merged).model_dump(mode="json", exclude_none=True)


def missing_fields(requirement: dict) -> list[str]:
    return [key for key in FIELD_LABELS if requirement.get(key) is None]


class TravelState(AgentState):
    current_step: NotRequired[PlanningStep]
    user_requirement: NotRequired[dict]
    missing_fields: NotRequired[list[str]]
    requirement_ready: NotRequired[bool]
    requirement_revision: NotRequired[int]
    requirement_confirmed: NotRequired[bool]
    confirmed_revision: NotRequired[int | None]
    selected_destination: NotRequired[str | None]
    transport_options: NotRequired[list[dict]]
    selected_transport: NotRequired[str | None]
    accommodation_options: NotRequired[list[dict]]
    selected_accommodation_types: NotRequired[list[str]]
    food_options: NotRequired[list[dict]]
    selected_food_types: NotRequired[list[str]]
    itinerary: NotRequired[list[dict] | None]
    budget: NotRequired[dict | None]
    report: NotRequired[str | None]
    last_transport_query: NotRequired[dict | None]

    planning_stops: NotRequired[list[dict]]
    planning_result: NotRequired[dict | None]
