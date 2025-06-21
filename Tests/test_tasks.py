from http import HTTPStatus

import factory.fuzzy
import pytest

from app.models.models import Task


class TaskFactory(factory.Factory):
    class Meta:
        model = Task

    title = factory.Faker('text')
    description = factory.Faker('text')
    state = factory.Faker('text')
    user_id = 1


def test_create_task(client, token):
    response = client.post(
        '/tasks',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'Teste titulo',
            'description': 'Teste desc',
            'state': 'criada',
        },
    )

    assert response.json() == {
        'id': 1,
        'title': 'Teste titulo',
        'description': 'Teste desc',
        'state': 'criada',
    }


@pytest.mark.asyncio
async def test_list_tasks_should_return_5_tasks(session, client, user, token):
    expected_tasks = 5
    session.add_all(TaskFactory.create_batch(5, user_id=user.id))
    await session.commit()
    response = client.get(
        '/tasks/', headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['tasks']) == expected_tasks


@pytest.mark.asyncio
async def test_list_tasks_pagination_should_return_2_tasks(
    session, client, user, token
):
    expected_tasks = 2
    session.add_all(TaskFactory.create_batch(5, user_id=user.id))
    await session.commit()
    response = client.get(
        '/tasks/?offset=1&limit=2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['tasks']) == expected_tasks


@pytest.mark.asyncio
async def test_list_tasks_filters_title(session, client, user, token):
    expected_tasks_title = 5
    session.add_all(
        TaskFactory.create_batch(5, user_id=user.id, title='Test task 1')
    )
    await session.commit()
    response = client.get(
        '/tasks/?title=Test task 1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['tasks']) == expected_tasks_title


@pytest.mark.asyncio
async def test_list_tasks_filters_desc(session, client, user, token):
    expected_tasks_desc = 5
    session.add_all(
        TaskFactory.create_batch(5, user_id=user.id, description='description')
    )
    await session.commit()
    response = client.get(
        '/tasks/?description=desc',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['tasks']) == expected_tasks_desc


@pytest.mark.asyncio
async def test_list_tasks_filters_combined(session, client, user, token):
    expected_tasks_desc_title = 5
    session.add_all(
        TaskFactory.create_batch(
            5,
            user_id=user.id,
            title='Test combinado',
            description='combina description',
            state='feita',
        )
    )

    session.add_all(
        TaskFactory.create_batch(
            3, title='Roxos', description='Purples', state='fazendo'
        )
    )
    await session.commit()
    response = client.get(
        '/tasks/?title=Test combinado&description=combina&state=feita',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['tasks']) == expected_tasks_desc_title


def test_patch_task_error(client, token):
    response = client.patch(
        '/tasks/10', json={}, headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Not Found'}


@pytest.mark.asyncio
async def test_patch_task(session, client, user, token):
    task = TaskFactory(user_id=user.id)

    session.add(task)
    await session.commit()

    response = client.patch(
        f'/tasks/{task.id}',
        json={
            'title': 'teste!',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['title'] == 'teste!'


def test_delete_error(client, token):
    response = client.delete(
        '/tasks/10',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Not Found'}


@pytest.mark.asyncio
async def test_delete_task(session, client, user, token):
    task = TaskFactory(user_id=user.id)
    session.add(task)
    await session.commit()

    response = client.delete(
        f'/tasks/{task.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Task has been delete successfully'}
