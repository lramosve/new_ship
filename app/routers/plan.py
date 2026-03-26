from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app import schemas
from app.models.plan import Plan as PlanModel
from app.db import get_db
from typing import List

router = APIRouter()


@router.post("/plans/", response_model=schemas.Plan)
def create_plan(plan: schemas.PlanCreate, db: Session = Depends(get_db)):
    db_plan = PlanModel(**plan.dict())
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan


@router.get("/plans/", response_model=List[schemas.Plan])
def read_plans(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    plans = db.query(PlanModel).offset(skip).limit(limit).all()
    return plans


@router.get("/plans/{plan_id}", response_model=schemas.Plan)
def read_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(PlanModel).filter(PlanModel.id == plan_id).first()
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@router.put("/plans/{plan_id}", response_model=schemas.Plan)
def update_plan(plan_id: int, plan: schemas.PlanUpdate, db: Session = Depends(get_db)):
    db_plan = db.query(PlanModel).filter(PlanModel.id == plan_id).first()
    if db_plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    update_data = plan.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_plan, key, value)
    db.commit()
    db.refresh(db_plan)
    return db_plan


@router.delete("/plans/{plan_id}", response_model=schemas.Plan)
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    db_plan = db.query(PlanModel).filter(PlanModel.id == plan_id).first()
    if db_plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    db.delete(db_plan)
    db.commit()
    return db_plan
