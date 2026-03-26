from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
import logging

from app import schemas, models
from app.db import get_db
from app.dependencies import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post('/projects/', response_model=schemas.Project, status_code=status.HTTP_201_CREATED)
def create_project(
    project: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    db_project = models.Project(name=project.name, description=project.description)
    logger.info(f'DEBUG: Creating project with data: {project}')
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@router.get('/projects/', response_model=schemas.ProjectList)
def read_projects(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    query = db.query(models.Project)
    total = query.count()
    projects = query.offset(skip).limit(limit).all()
    return schemas.ProjectList(items=projects, total=total)


@router.get('/projects/{project_id}', response_model=schemas.Project)
def read_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail='Project not found')
    return project


@router.put('/projects/{project_id}', response_model=schemas.Project)
def update_project(
    project_id: int,
    project: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail='Project not found')
    db_project.name = project.name
    db_project.description = project.description
    db.commit()
    db.refresh(db_project)
    return db_project


@router.delete('/projects/{project_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail='Project not found')
    db.delete(db_project)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
