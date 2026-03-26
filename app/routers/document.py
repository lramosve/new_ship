from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app import schemas
from app.db import get_db
from app.dependencies import get_current_user
from app.models.document import Document as DocumentModel

router = APIRouter()


@router.post('/documents/', response_model=schemas.Document, status_code=status.HTTP_201_CREATED)
def create_document(
    document: schemas.DocumentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    db_document = DocumentModel(**document.model_dump(), owner_id=current_user.id)
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


@router.get('/documents/', response_model=schemas.DocumentList)
def read_documents(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    query = db.query(DocumentModel)
    total = query.count()
    documents: List[DocumentModel] = query.offset(skip).limit(limit).all()
    return schemas.DocumentList(items=documents, total=total)


@router.get('/documents/{document_id}', response_model=schemas.Document)
def read_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if document is None:
        raise HTTPException(status_code=404, detail='Document not found')
    return document


@router.put('/documents/{document_id}', response_model=schemas.Document)
def update_document(
    document_id: int,
    document: schemas.DocumentUpdate,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    db_document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if db_document is None:
        raise HTTPException(status_code=404, detail='Document not found')
    update_data = document.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_document, key, value)
    db.commit()
    db.refresh(db_document)
    return db_document


@router.delete('/documents/{document_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    db_document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if db_document is None:
        raise HTTPException(status_code=404, detail='Document not found')
    db.delete(db_document)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
