from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app import schemas
from app.db import get_db
from app.dependencies import get_current_user
from app.models.issue import Issue as IssueModel

router = APIRouter()


@router.post('/issues/', response_model=schemas.Issue, status_code=status.HTTP_201_CREATED)
def create_issue(
    issue: schemas.IssueCreate,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    db_issue = IssueModel(**issue.model_dump())
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    return db_issue


@router.get('/issues/', response_model=schemas.IssueList)
def read_issues(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    query = db.query(IssueModel)
    total = query.count()
    issues: List[IssueModel] = query.offset(skip).limit(limit).all()
    return schemas.IssueList(items=issues, total=total)


@router.get('/issues/{issue_id}', response_model=schemas.Issue)
def read_issue(issue_id: int, db: Session = Depends(get_db)):
    issue = db.query(IssueModel).filter(IssueModel.id == issue_id).first()
    if issue is None:
        raise HTTPException(status_code=404, detail='Issue not found')
    return issue


@router.put('/issues/{issue_id}', response_model=schemas.Issue)
def update_issue(
    issue_id: int,
    issue: schemas.IssueUpdate,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    db_issue = db.query(IssueModel).filter(IssueModel.id == issue_id).first()
    if db_issue is None:
        raise HTTPException(status_code=404, detail='Issue not found')
    update_data = issue.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_issue, key, value)
    db.commit()
    db.refresh(db_issue)
    return db_issue


@router.delete('/issues/{issue_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    db_issue = db.query(IssueModel).filter(IssueModel.id == issue_id).first()
    if db_issue is None:
        raise HTTPException(status_code=404, detail='Issue not found')
    db.delete(db_issue)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
