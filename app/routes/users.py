import http
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.database import get_session
from app.controllers.security import (
    get_current_user,
    get_password_hash,
)
from app.models.models import User
from app.models.schemas import (
    FilterPage,
    Message,
    UserList,
    UserPublic,
    UserSchema,
)

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
router = APIRouter(prefix='/users', tags=['Usuários'])


@router.get('/', status_code=http.HTTPStatus.OK, response_model=UserList)
async def read_user(
    session: Session,
    filters: Annotated[FilterPage, Query()],
):
    query = await session.scalars(
        select(User).offset(filters.offset).limit(filters.limit)
    )
    user_list = query.all()
    return {'users': user_list}


@router.post(
    '/', status_code=http.HTTPStatus.CREATED, response_model=UserPublic
)
async def create_user(user: UserSchema, session: Session):
    db_user = await session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                detail='Username already exists',
                status_code=http.HTTPStatus.CONFLICT,
            )
        elif db_user.email == user.email:
            raise HTTPException(
                detail='Email already exists',
                status_code=http.HTTPStatus.CONFLICT,
            )
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username, email=user.email, password=hashed_password
    )

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


@router.put('/{user_id}', response_model=UserPublic)
async def update_user(
    user_id: int,
    user: UserSchema,
    session: Session,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            detail='Not enough permissions', status_code=HTTPStatus.FORBIDDEN
        )
    try:
        current_user.username = user.username
        current_user.password = get_password_hash(user.password)
        current_user.email = user.email
        await session.commit()
        await session.refresh(current_user)

        return current_user
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or Email already exists',
        )


@router.delete(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=Message,
)
async def delete_user(
    user_id: int,
    session: Session,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            detail='Not enough permissions', status_code=HTTPStatus.FORBIDDEN
        )
    await session.delete(current_user)
    await session.commit()

    return {'message': 'User deleted'}


@router.get(
    '/{user_id}',
    status_code=http.HTTPStatus.OK,
    response_model=UserPublic,
)
async def read_user_by_id(user_id: int, session: Session):
    user_db = await session.scalar(select(User).where(User.id == user_id))
    if not user_db:
        raise HTTPException(
            detail='User not found', status_code=HTTPStatus.NOT_FOUND
        )
    else:
        return user_db
