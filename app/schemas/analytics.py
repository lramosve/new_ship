from datetime import date

from pydantic import BaseModel

from .task import TaskStatus


class AnalyticsSummary(BaseModel):
    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    overdue_tasks: int
    completion_rate: int
    average_progress: int


class TaskTrendPoint(BaseModel):
    date: date
    created_tasks: int
    completed_tasks: int


class TaskStatusDistribution(BaseModel):
    status: TaskStatus
    label: str
    count: int


class PriorityDistribution(BaseModel):
    priority: str
    label: str
    count: int


class ProjectProgressSnapshot(BaseModel):
    project_id: int | None
    project_name: str
    total_tasks: int
    completed_tasks: int
    average_progress: int
    completion_rate: int


class AnalyticsOverview(BaseModel):
    summary: AnalyticsSummary
    task_trends: list[TaskTrendPoint]
    status_distribution: list[TaskStatusDistribution]
    priority_distribution: list[PriorityDistribution]
    project_progress: list[ProjectProgressSnapshot]
