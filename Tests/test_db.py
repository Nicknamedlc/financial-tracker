from dataclasses import asdict

import pytest
from sqlalchemy import select

from app.models.models import Task, User


@pytest.mark.asyncio
async def test_create_user_without_task(session, mock_db_time, user):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='test', email='teste@teste.com', password='secret'
        )

        session.add(new_user)
        await session.commit()

    user = await session.scalar(select(User).where(User.username == 'test'))

    assert asdict(user) == {
        'id': 2,
        'username': 'test',
        'email': 'teste@teste.com',
        'password': 'secret',
        'created_at': time,
        'updated_at': time,
        'tasks': [],
    }


@pytest.mark.asyncio
async def test_create_task(session, user):
    task = Task(
        title='Teste titulo',
        description='Teste desc',
        state='designada',
        user_id=user.id,
    )

    session.add(task)
    await session.commit()

    task = await session.scalar(select(Task))

    assert asdict(task) == {
        'title': 'Teste titulo',
        'description': 'Teste desc',
        'state': 'designada',
        'id': 1,
        'user_id': 1,
    }


@pytest.mark.asyncio
async def test_user_task_relationship(session, user: User):
    task = Task(
        title='Teste titulo',
        description='Teste desc',
        state='designada',
        user_id=user.id,
    )
    session.add(task)
    await session.commit()
    await session.refresh(user)

    user = await session.scalar(select(User).where(User.id == user.id))

    assert user.tasks == [task]
