from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app import schemas
from app.models.document import Document as DocumentModel
from app.db import get_db
from typing import List

router = APIRouter()


@router.post("/documents/", response_model=schemas.Document)
def create_document(document: schemas.DocumentCreate, db: Session = Depends(get_db)):
    db_document = DocumentModel(**document.dict())
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


@router.get("/documents/", response_model=List[schemas.Document])
def read_documents(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    documents = db.query(DocumentModel).offset(skip).limit(limit).all()
    return documents


@router.get("/documents/{document_id}", response_model=schemas.Document)
def read_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.put("/documents/{document_id}", response_model=schemas.Document)
def update_document(document_id: int, document: schemas.DocumentUpdate, db: Session = Depends(get_db)):
    db_document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if db_document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    update_data = document.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_document, key, value)
    db.commit()
    db.refresh(db_document)
    return db_document


@router.delete("/documents/{document_id}", response_model=schemas.Document)
def delete_document(document_id: int, db: Session = Depends(get_db)):
    db_document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if db_document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(db_document)
    db.commit()
    return db_document
