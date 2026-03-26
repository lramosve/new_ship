from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


IssueStatus = Literal['open', 'in_progress', 'blocked', 'closed']


class IssueBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    status: IssueStatus


class IssueCreate(IssueBase):
    pass


class IssueUpdate(IssueBase):
    pass


class IssueList(BaseModel):
    items: list['Issue']
    total: int


class IssueInDBBase(IssueBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class Issue(IssueInDBBase):
    pass
