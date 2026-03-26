from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .project import Project
from .user import User

TaskStatus = Literal['todo', 'in_progress', 'in_review', 'done']
TaskPriority = Literal['low', 'medium', 'high', 'urgent']


class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    status: TaskStatus = 'todo'
    priority: TaskPriority = 'medium'
    progress: int = Field(default=0, ge=0, le=100)
    start_date: date | None = None
    due_date: date | None = None
    project_id: int | None = Field(default=None, ge=1)
    assignee_id: int | None = Field(default=None, ge=1)

    @model_validator(mode='after')
    def validate_dates(self):
        if self.start_date and self.due_date and self.start_date > self.due_date:
            raise ValueError('start_date cannot be after due_date')
        return self


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    pass


class TaskList(BaseModel):
    items: list['Task']
    total: int


class TaskInDBBase(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime
    project: Project | None = None
    assignee: User | None = None

    model_config = ConfigDict(from_attributes=True)


class Task(TaskInDBBase):
    pass
