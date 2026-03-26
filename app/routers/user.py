from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app import schemas
from app.core.security import hash_password
from app.db import get_db
from app.dependencies import get_current_user
from app.models.user import User as UserModel

router = APIRouter()


@router.post('/users/', response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if existing_user is not None:
        raise HTTPException(status_code=400, detail='A user with that email already exists')

    db_user = UserModel(
        name=user.name,
        email=user.email,
        hashed_password=hash_password(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get('/users/', response_model=schemas.UserList)
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    query = db.query(UserModel)
    total = query.count()
    users: List[UserModel] = query.offset(skip).limit(limit).all()
    return schemas.UserList(items=users, total=total)


@router.get('/users/me', response_model=schemas.AuthenticatedUser)
def read_current_user(current_user: UserModel = Depends(get_current_user)):
    return schemas.AuthenticatedUser(id=current_user.id, name=current_user.name, email=current_user.email)


@router.get('/users/{user_id}', response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail='User not found')
    return user


@router.put('/users/{user_id}', response_model=schemas.User)
def update_user(
    user_id: int,
    user: schemas.UserUpdate,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail='User not found')

    existing_user = db.query(UserModel).filter(UserModel.email == user.email, UserModel.id != user_id).first()
    if existing_user is not None:
        raise HTTPException(status_code=400, detail='A user with that email already exists')

    db_user.name = user.name
    db_user.email = user.email
    if user.password:
        db_user.hashed_password = hash_password(user.password)

    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete('/users/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail='User not found')
    db.delete(db_user)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
