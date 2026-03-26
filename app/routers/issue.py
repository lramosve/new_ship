from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app import schemas
from app.models.issue import Issue as IssueModel
from app.db import get_db
from typing import List

router = APIRouter()


@router.post("/issues/", response_model=schemas.Issue)
def create_issue(issue: schemas.IssueCreate, db: Session = Depends(get_db)):
    db_issue = IssueModel(**issue.dict())
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    return db_issue


@router.get("/issues/", response_model=List[schemas.Issue])
def read_issues(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    issues = db.query(IssueModel).offset(skip).limit(limit).all()
    return issues


@router.get("/issues/{issue_id}", response_model=schemas.Issue)
def read_issue(issue_id: int, db: Session = Depends(get_db)):
    issue = db.query(IssueModel).filter(IssueModel.id == issue_id).first()
    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue


@router.put("/issues/{issue_id}", response_model=schemas.Issue)
def update_issue(issue_id: int, issue: schemas.IssueUpdate, db: Session = Depends(get_db)):
    db_issue = db.query(IssueModel).filter(IssueModel.id == issue_id).first()
    if db_issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")
    update_data = issue.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_issue, key, value)
    db.commit()
    db.refresh(db_issue)
    return db_issue


@router.delete("/issues/{issue_id}", response_model=schemas.Issue)
def delete_issue(issue_id: int, db: Session = Depends(get_db)):
    db_issue = db.query(IssueModel).filter(IssueModel.id == issue_id).first()
    if db_issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")
    db.delete(db_issue)
    db.commit()
    return db_issue
