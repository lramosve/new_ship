from datetime import datetime
from pydantic import BaseModel, Field


class PlanBase(BaseModel):
    description: str = Field(min_length=1, max_length=1000)
    week_number: int = Field(ge=1, le=53)


class PlanCreate(PlanBase):
    pass


class PlanUpdate(PlanBase):
    pass


class PlanList(BaseModel):
    items: list['Plan']
    total: int


class PlanInDBBase(PlanBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class Plan(PlanInDBBase):
    pass
