from datetime import date, timedelta
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, model_validator

class Stop(BaseModel):
    model_config=ConfigDict(extra="forbid")
    city: str=Field(min_length=1,max_length=80)
    days: int=Field(ge=1,le=15)

class PlanRequest(BaseModel):
    model_config=ConfigDict(extra="forbid")
    session_id: UUID
    departure_city: str=Field(min_length=1,max_length=80)
    departure_date: date
    stops: list[Stop]=Field(min_length=1,max_length=5)
    adults: int=Field(default=1,ge=1,le=10)
    children: int=Field(default=0,ge=0,le=10)
    budget_per_person: float=Field(gt=0,le=1000000,allow_inf_nan=False)
    styles: list[str]=Field(default_factory=list,max_length=8)
    hotel_per_night: float=Field(default=300,ge=0,le=100000,allow_inf_nan=False)
    meal_per_person_day: float=Field(default=100,ge=0,le=10000,allow_inf_nan=False)
    auto_confirm: bool=False
    mode: Literal["fast","sequential"]="fast"
    @model_validator(mode="after")
    def duration(self):
        if sum(s.days for s in self.stops)>30:raise ValueError("行程最多30天")
        return self
    def legs(self):
        city=self.departure_city; day=self.departure_date; rows=[]
        for index,stop in enumerate(self.stops):
            if city!=stop.city:
                rows.append({"leg_id":f"leg-{index}","fromStation":city,"toStation":stop.city,"date":day.isoformat()})
            city=stop.city;day+=timedelta(days=stop.days)
        return rows

class DayPlan(BaseModel):
    model_config=ConfigDict(extra="forbid")
    day: int=Field(ge=1,le=30)
    city: str
    morning: str
    afternoon: str
    evening: str
    notes: str=""

class GeneratedPlan(BaseModel):
    model_config=ConfigDict(extra="forbid")
    days: list[DayPlan]=Field(min_length=1,max_length=30)
    summary: str

class SelectionRequest(BaseModel):
    revision: int=Field(ge=0)
    option_id: str=Field(min_length=1,max_length=100)

class PreferencePatch(BaseModel):
    model_config=ConfigDict(extra="forbid")
    travel_styles: list[str] | None=Field(default=None,max_length=8)
    dietary_needs: str | None=Field(default=None,max_length=500)
    hotel_type: str | None=Field(default=None,max_length=100)
    pace: Literal["轻松","适中","紧凑"] | None=None
