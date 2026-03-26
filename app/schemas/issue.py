from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class IssueBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str


class IssueCreate(IssueBase):
    pass


class IssueUpdate(IssueBase):
    pass


class IssueInDBBase(IssueBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class ConfigDict:
        from_attributes = True


class Issue(IssueInDBBase):
    pass
