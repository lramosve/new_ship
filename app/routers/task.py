from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session, joinedload

from app import schemas
from app.db import get_db
from app.dependencies import get_current_user
from app.models.project import Project as ProjectModel
from app.models.task import Task as TaskModel
from app.models.user import User as UserModel

router = APIRouter()


def validate_relationships(db: Session, project_id: int | None, assignee_id: int | None):
    if project_id is not None:
        project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
        if project is None:
            raise HTTPException(status_code=400, detail='Project not found for task')
    if assignee_id is not None:
        assignee = db.query(UserModel).filter(UserModel.id == assignee_id).first()
        if assignee is None:
            raise HTTPException(status_code=400, detail='Assignee not found for task')


def serialize_task(task: TaskModel) -> dict[str, Any]:
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


@router.post('/tasks/', response_model=schemas.Task, status_code=status.HTTP_201_CREATED)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    validate_relationships(db, task.project_id, task.assignee_id)
    db_task = TaskModel(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    task_with_relations = db.query(TaskModel).options(joinedload(TaskModel.project), joinedload(TaskModel.assignee)).filter(TaskModel.id == db_task.id).first()
    return serialize_task(task_with_relations)


@router.get('/tasks/', response_model=schemas.TaskList)
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    total = db.query(TaskModel).count()
    tasks: List[TaskModel] = (
        db.query(TaskModel)
        .options(joinedload(TaskModel.project), joinedload(TaskModel.assignee))
        .order_by(TaskModel.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return {'items': [serialize_task(task) for task in tasks], 'total': total}


@router.get('/tasks/{task_id}', response_model=schemas.Task)
def read_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(TaskModel).options(joinedload(TaskModel.project), joinedload(TaskModel.assignee)).filter(TaskModel.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail='Task not found')
    return serialize_task(task)


@router.put('/tasks/{task_id}', response_model=schemas.Task)
def update_task(
    task_id: int,
    task: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    db_task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail='Task not found')

    validate_relationships(db, task.project_id, task.assignee_id)
    update_data = task.model_dump()
    for key, value in update_data.items():
        setattr(db_task, key, value)

    db.commit()
    db.refresh(db_task)
    task_with_relations = db.query(TaskModel).options(joinedload(TaskModel.project), joinedload(TaskModel.assignee)).filter(TaskModel.id == task_id).first()
    return serialize_task(task_with_relations)


@router.delete('/tasks/{task_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    db_task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail='Task not found')
    db.delete(db_task)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
