from datetime import date

from pydantic import BaseModel

from .task import Task, TaskStatus


class KanbanColumn(BaseModel):
    status: TaskStatus
    label: str
    count: int
    tasks: list[Task]


class GanttTask(BaseModel):
    task: Task
    start_date: date
    due_date: date
    duration_days: int
    offset_days: int


class AssignmentSummary(BaseModel):
    assignee_id: int | None
    assignee_name: str
    total_tasks: int
    todo_tasks: int
    in_progress_tasks: int
    completed_tasks: int
    avg_progress: int


class TimelineBounds(BaseModel):
    start_date: date | None
    end_date: date | None
    total_days: int


class ProjectManagementSummary(BaseModel):
    total_projects: int
    total_tasks: int
    unassigned_tasks: int
    overdue_tasks: int
    completed_tasks: int
    completion_rate: int


class ProjectManagementOverview(BaseModel):
    summary: ProjectManagementSummary
    kanban: list[KanbanColumn]
    gantt: list[GanttTask]
    assignment_workload: list[AssignmentSummary]
    timeline: TimelineBounds
