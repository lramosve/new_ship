from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PlanBase(BaseModel):
    description: str
    week_number: int


class PlanCreate(PlanBase):
    pass


class PlanUpdate(PlanBase):
    pass


class PlanInDBBase(PlanBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class ConfigDict:
        from_attributes = True


class Plan(PlanInDBBase):
    pass
