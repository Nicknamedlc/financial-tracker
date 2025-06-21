from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.database import get_session
from app.controllers.security import get_current_user
from app.models.models import Task, User
from app.models.schemas import (
    FilterTask,
    Message,
    TaskList,
    TaskPublic,
    TaskSchema,
    TaskUpdate,
)

router = APIRouter(prefix='/tasks', tags=['Tarefas'])
Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', response_model=TaskPublic)
async def crate_task(
    task: TaskSchema,
    user: CurrentUser,
    session: Session,
):
    task_db = Task(
        title=task.title,
        description=task.description,
        state=task.state,
        user_id=user.id,
    )
    session.add(task_db)
    await session.commit()
    await session.refresh(task_db)

    return task_db


@router.get('/', response_model=TaskList)
async def list_tasks(
    session: Session,
    user: CurrentUser,
    task_filter: Annotated[FilterTask, Query()],
):
    query = select(Task).where(Task.user_id == user.id)
    if task_filter.title:
        query = query.filter(Task.title.contains(task_filter.title))
    if task_filter.description:
        query = query.filter(
            Task.description.contains(task_filter.description)
        )
    if task_filter.state:
        query = query.filter(Task.state.contains(task_filter.state))

    tasks = await session.scalars(
        query.offset(task_filter.offset).limit(task_filter.limit)
    )

    return {'tasks': tasks.all()}


@router.patch('/{task_id}', response_model=TaskPublic)
async def patch_task(
    task_id: int, session: Session, user: CurrentUser, task: TaskUpdate
):
    task_db = await session.scalar(
        select(Task).where(Task.id == task_id, user.id == Task.user_id)
    )
    if not task_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Not Found'
        )
    for (
        key,
        value,
    ) in task.model_dump(exclude_unset=True).items():
        setattr(task_db, key, value)

    session.add(task_db)
    await session.commit()
    await session.refresh(task_db)

    return task_db


@router.delete('/{task_id}', response_model=Message)
async def delete_task(
    task_id: int,
    session: Session,
    user: CurrentUser,
):
    task = await session.scalar(
        select(Task).where(Task.id == task_id, Task.user_id == user.id)
    )
    if not task:
        raise HTTPException(
            detail='Not Found', status_code=HTTPStatus.NOT_FOUND
        )
    await session.delete(task)
    await session.commit()

    return {'message': 'Task has been delete successfully'}
