from collections import Counter, defaultdict
from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.db import get_db
from app.models.project import Project
from app.models.task import Task
from app.schemas.analytics import (
    AnalyticsOverview,
    AnalyticsSummary,
    PriorityDistribution,
    ProjectProgressSnapshot,
    TaskStatusDistribution,
    TaskTrendPoint,
)

router = APIRouter(prefix='/analytics', tags=['Analytics'])

STATUS_ORDER = ['todo', 'in_progress', 'in_review', 'done']
STATUS_LABELS = {
    'todo': 'To Do',
    'in_progress': 'In Progress',
    'in_review': 'In Review',
    'done': 'Done',
}

PRIORITY_ORDER = ['low', 'medium', 'high', 'urgent']
PRIORITY_LABELS = {
    'low': 'Low',
    'medium': 'Medium',
    'high': 'High',
    'urgent': 'Urgent',
}


@router.get('/overview', response_model=AnalyticsOverview)
def get_analytics_overview(db: Session = Depends(get_db)):
    tasks = (
        db.query(Task)
        .options(joinedload(Task.project), joinedload(Task.assignee))
        .order_by(Task.created_at.asc(), Task.id.asc())
        .all()
    )
    projects = db.query(Project).order_by(Project.name.asc(), Project.id.asc()).all()

    today = date.today()
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task.status == 'done')
    in_progress_tasks = sum(1 for task in tasks if task.status == 'in_progress')
    overdue_tasks = sum(1 for task in tasks if task.due_date and task.due_date < today and task.status != 'done')
    completion_rate = round((completed_tasks / total_tasks) * 100) if total_tasks else 0
    average_progress = round(sum(task.progress for task in tasks) / total_tasks) if total_tasks else 0

    created_counts: dict[date, int] = defaultdict(int)
    completed_counts: dict[date, int] = defaultdict(int)
    trend_dates: list[date] = []
    for task in tasks:
        created_day = task.created_at.date()
        created_counts[created_day] += 1
        trend_dates.append(created_day)
        if task.status == 'done':
            completed_day = task.updated_at.date()
            completed_counts[completed_day] += 1
            trend_dates.append(completed_day)

    if trend_dates:
        trend_start = min(trend_dates)
        trend_end = max(trend_dates)
    else:
        trend_end = today
        trend_start = trend_end - timedelta(days=6)

    task_trends: list[TaskTrendPoint] = []
    cursor = trend_start
    while cursor <= trend_end:
        task_trends.append(
            TaskTrendPoint(
                date=cursor,
                created_tasks=created_counts.get(cursor, 0),
                completed_tasks=completed_counts.get(cursor, 0),
            )
        )
        cursor += timedelta(days=1)

    status_counts = Counter(task.status for task in tasks)
    status_distribution = [
        TaskStatusDistribution(
            status=status,
            label=STATUS_LABELS[status],
            count=status_counts.get(status, 0),
        )
        for status in STATUS_ORDER
    ]

    priority_counts = Counter((task.priority or 'medium') for task in tasks)
    priority_distribution = [
        PriorityDistribution(
            priority=priority,
            label=PRIORITY_LABELS[priority],
            count=priority_counts.get(priority, 0),
        )
        for priority in PRIORITY_ORDER
    ]

    tasks_by_project: dict[int | None, list[Task]] = defaultdict(list)
    for task in tasks:
        tasks_by_project[task.project_id].append(task)

    project_progress: list[ProjectProgressSnapshot] = []
    for project in projects:
        project_tasks = tasks_by_project.get(project.id, [])
        project_total = len(project_tasks)
        project_completed = sum(1 for task in project_tasks if task.status == 'done')
        project_average_progress = round(sum(task.progress for task in project_tasks) / project_total) if project_total else 0
        project_completion_rate = round((project_completed / project_total) * 100) if project_total else 0
        project_progress.append(
            ProjectProgressSnapshot(
                project_id=project.id,
                project_name=project.name,
                total_tasks=project_total,
                completed_tasks=project_completed,
                average_progress=project_average_progress,
                completion_rate=project_completion_rate,
            )
        )

    unassigned_tasks = tasks_by_project.get(None, [])
    if unassigned_tasks:
        unassigned_total = len(unassigned_tasks)
        unassigned_completed = sum(1 for task in unassigned_tasks if task.status == 'done')
        unassigned_average_progress = round(sum(task.progress for task in unassigned_tasks) / unassigned_total) if unassigned_total else 0
        unassigned_completion_rate = round((unassigned_completed / unassigned_total) * 100) if unassigned_total else 0
        project_progress.append(
            ProjectProgressSnapshot(
                project_id=None,
                project_name='Unassigned',
                total_tasks=unassigned_total,
                completed_tasks=unassigned_completed,
                average_progress=unassigned_average_progress,
                completion_rate=unassigned_completion_rate,
            )
        )

    return AnalyticsOverview(
        summary=AnalyticsSummary(
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            in_progress_tasks=in_progress_tasks,
            overdue_tasks=overdue_tasks,
            completion_rate=completion_rate,
            average_progress=average_progress,
        ),
        task_trends=task_trends,
        status_distribution=status_distribution,
        priority_distribution=priority_distribution,
        project_progress=project_progress,
    )
