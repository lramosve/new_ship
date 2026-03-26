from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app import schemas
from app.db import get_db
from app.models.project import Project as ProjectModel
from app.models.task import Task as TaskModel

router = APIRouter(prefix='/project-management', tags=['project-management'])

KANBAN_LABELS: dict[schemas.TaskStatus, str] = {
    'todo': 'To do',
    'in_progress': 'In progress',
    'in_review': 'In review',
    'done': 'Done',
}


def serialize_task(task: TaskModel) -> dict:
    return {
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'status': task.status,
        'priority': task.priority,
        'progress': task.progress,
        'start_date': task.start_date,
        'due_date': task.due_date,
        'project_id': task.project_id,
        'assignee_id': task.assignee_id,
        'created_at': task.created_at,
        'updated_at': task.updated_at,
        'project': (
            {
                'id': task.project.id,
                'name': task.project.name,
                'description': task.project.description,
            }
            if task.project is not None
            else None
        ),
        'assignee': (
            {
                'id': task.assignee.id,
                'name': task.assignee.name,
                'email': task.assignee.email,
                'created_at': task.assignee.created_at,
                'updated_at': task.assignee.updated_at,
            }
            if task.assignee is not None
            else None
        ),
    }


@router.get('/overview', response_model=schemas.ProjectManagementOverview)
def read_project_management_overview(db: Session = Depends(get_db)):
    tasks = (
        db.query(TaskModel)
        .options(joinedload(TaskModel.project), joinedload(TaskModel.assignee))
        .order_by(TaskModel.id.desc())
        .all()
    )
    total_projects = db.query(ProjectModel).count()
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task.status == 'done')
    unassigned_tasks = sum(1 for task in tasks if task.assignee_id is None)
    today = date.today()
    overdue_tasks = sum(1 for task in tasks if task.due_date is not None and task.due_date < today and task.status != 'done')
    completion_rate = round((completed_tasks / total_tasks) * 100) if total_tasks else 0

    kanban = []
    for status, label in KANBAN_LABELS.items():
        column_tasks = [serialize_task(task) for task in tasks if task.status == status]
        kanban.append(
            {
                'status': status,
                'label': label,
                'count': len(column_tasks),
                'tasks': column_tasks,
            }
        )

    scheduled_tasks = [task for task in tasks if task.start_date is not None and task.due_date is not None]
    gantt = []
    timeline_start = None
    timeline_end = None
    total_days = 0
    if scheduled_tasks:
        timeline_start = min(task.start_date for task in scheduled_tasks)
        timeline_end = max(task.due_date for task in scheduled_tasks)
        total_days = max(1, (timeline_end - timeline_start).days + 1)
        for task in sorted(scheduled_tasks, key=lambda item: (item.start_date, item.id)):
            gantt.append(
                {
                    'task': serialize_task(task),
                    'start_date': task.start_date,
                    'due_date': task.due_date,
                    'duration_days': max(1, (task.due_date - task.start_date).days + 1),
                    'offset_days': (task.start_date - timeline_start).days,
                }
            )

    assignment_map: dict[int | None, dict[str, int | str | None]] = {}
    for task in tasks:
        assignee_id = task.assignee.id if task.assignee is not None else None
        assignee_name = task.assignee.name if task.assignee is not None else 'Unassigned'
        bucket = assignment_map.setdefault(
            assignee_id,
            {
                'assignee_id': assignee_id,
                'assignee_name': assignee_name,
                'total_tasks': 0,
                'todo_tasks': 0,
                'in_progress_tasks': 0,
                'completed_tasks': 0,
                'progress_total': 0,
            },
        )
        bucket['total_tasks'] += 1
        bucket['progress_total'] += task.progress
        if task.status == 'todo':
            bucket['todo_tasks'] += 1
        if task.status in {'in_progress', 'in_review'}:
            bucket['in_progress_tasks'] += 1
        if task.status == 'done':
            bucket['completed_tasks'] += 1

    assignment_workload = []
    for bucket in assignment_map.values():
        total = int(bucket['total_tasks'])
        avg_progress = round(int(bucket['progress_total']) / total) if total else 0
        assignment_workload.append(
            {
                'assignee_id': bucket['assignee_id'],
                'assignee_name': bucket['assignee_name'],
                'total_tasks': total,
                'todo_tasks': int(bucket['todo_tasks']),
                'in_progress_tasks': int(bucket['in_progress_tasks']),
                'completed_tasks': int(bucket['completed_tasks']),
                'avg_progress': avg_progress,
            }
        )
    assignment_workload.sort(key=lambda item: (-item['total_tasks'], item['assignee_name']))

    return {
        'summary': {
            'total_projects': total_projects,
            'total_tasks': total_tasks,
            'unassigned_tasks': unassigned_tasks,
            'overdue_tasks': overdue_tasks,
            'completed_tasks': completed_tasks,
            'completion_rate': completion_rate,
        },
        'kanban': kanban,
        'gantt': gantt,
        'assignment_workload': assignment_workload,
        'timeline': {
            'start_date': timeline_start,
            'end_date': timeline_end,
            'total_days': total_days,
        },
    }
