from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app import schemas
from app.db import get_db
from app.dependencies import get_current_user
from app.models.plan import Plan as PlanModel

router = APIRouter()


@router.post('/plans/', response_model=schemas.Plan, status_code=status.HTTP_201_CREATED)
def create_plan(
    plan: schemas.PlanCreate,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    db_plan = PlanModel(**plan.model_dump())
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan


@router.get('/plans/', response_model=schemas.PlanList)
def read_plans(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    query = db.query(PlanModel)
    total = query.count()
    plans: List[PlanModel] = query.offset(skip).limit(limit).all()
    return schemas.PlanList(items=plans, total=total)


@router.get('/plans/{plan_id}', response_model=schemas.Plan)
def read_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(PlanModel).filter(PlanModel.id == plan_id).first()
    if plan is None:
        raise HTTPException(status_code=404, detail='Plan not found')
    return plan


@router.put('/plans/{plan_id}', response_model=schemas.Plan)
def update_plan(
    plan_id: int,
    plan: schemas.PlanUpdate,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    db_plan = db.query(PlanModel).filter(PlanModel.id == plan_id).first()
    if db_plan is None:
        raise HTTPException(status_code=404, detail='Plan not found')
    update_data = plan.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_plan, key, value)
    db.commit()
    db.refresh(db_plan)
    return db_plan


@router.delete('/plans/{plan_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    db_plan = db.query(PlanModel).filter(PlanModel.id == plan_id).first()
    if db_plan is None:
        raise HTTPException(status_code=404, detail='Plan not found')
    db.delete(db_plan)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
