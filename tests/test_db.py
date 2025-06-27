from dataclasses import asdict

import pytest
from sqlalchemy import select

from src.app.models.models import Transaction, User


@pytest.mark.asyncio
async def test_create_user_without_transaction(session, mock_db_time, user):
    with mock_db_time(model=User) as time:
        new_user = User(username='test', email='teste@teste.com', password='secret')

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
        'transactions': [],
    }


@pytest.mark.asyncio
async def test_create_transaction(session, user):
    transaction = Transaction(
        title='Teste titulo',
        description='Teste desc',
        state='designada',
        user_id=user.id,
        value=500,
    )

    session.add(transaction)
    await session.commit()

    transaction = await session.scalar(select(Transaction))

    assert asdict(transaction) == {
        'title': 'Teste titulo',
        'description': 'Teste desc',
        'state': 'designada',
        'id': 1,
        'user_id': 1,
        'value': 500.00,
    }


@pytest.mark.asyncio
async def test_user_transaction_relationship(session, user: User):
    transaction = Transaction(
        title='Teste titulo',
        description='Teste desc',
        state='designada',
        user_id=user.id,
        value=500.00,
    )
    session.add(transaction)
    await session.commit()
    await session.refresh(user)

    user = await session.scalar(select(User).where(User.id == user.id))

    assert user.transactions == [transaction]
