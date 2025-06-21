from contextlib import contextmanager
from datetime import datetime

import factory
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.app import app
from app.controllers.database import get_session
from app.controllers.security import get_password_hash
from app.controllers.settings import Settings
from app.models.models import User, table_registry


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'texto{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@texto.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')


@pytest_asyncio.fixture
async def user(session):
    password = 'texto'
    user = UserFactory(
        password=get_password_hash(password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password
    return user


@pytest_asyncio.fixture
async def other_user(session):
    password = 'texto'
    other_user = UserFactory(
        password=get_password_hash(password),
    )
    session.add(other_user)
    await session.commit()
    await session.refresh(other_user)

    other_user.clean_password = password
    return other_user


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope='session')
def engine():
    with PostgresContainer('postgres:16', driver='psycopg') as postgres:
        _engine = create_async_engine(postgres.get_connection_url())
        yield _engine


@pytest_asyncio.fixture
async def session(engine):
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)
    async with AsyncSession(engine, expire_on_commit=False) as s:
        yield s
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@contextmanager
def _mock_db_time(*, model=User, time=datetime.now()):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(User, 'before_insert', fake_time_hook)

    yield time

    event.remove(User, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest.fixture
def token(user, client):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    return response.json()['access_token']


@pytest.fixture
def settings():
    return Settings()
