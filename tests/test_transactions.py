from http import HTTPStatus

import factory.fuzzy
import pytest

from src.app.models.models import Transaction


class TransactionFactory(factory.Factory):
    class Meta:
        model = Transaction

    title = factory.Faker('text')
    description = factory.Faker('text')
    state = factory.Faker('text')
    user_id = 1


def test_create_transaction(client, token):
    response = client.post(
        '/transactions',
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
async def test_list_transactions_should_return_5_transactions(
    session, client, user, token
):
    expected_transactions = 5
    session.add_all(TransactionFactory.create_batch(5, user_id=user.id))
    await session.commit()
    response = client.get('/transactions/', headers={'Authorization': f'Bearer {token}'})

    assert len(response.json()['transactions']) == expected_transactions


@pytest.mark.asyncio
async def test_list_transactions_pagination_should_return_2_transactions(
    session, client, user, token
):
    expected_transactions = 2
    session.add_all(TransactionFactory.create_batch(5, user_id=user.id))
    await session.commit()
    response = client.get(
        '/transactions/?offset=1&limit=2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['transactions']) == expected_transactions


@pytest.mark.asyncio
async def test_list_transactions_filters_title(session, client, user, token):
    expected_transactions_title = 5
    session.add_all(
        TransactionFactory.create_batch(5, user_id=user.id, title='Test transaction 1')
    )
    await session.commit()
    response = client.get(
        '/transactions/?title=Test transaction 1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['transactions']) == expected_transactions_title


@pytest.mark.asyncio
async def test_list_transactions_filters_desc(session, client, user, token):
    expected_transactions_desc = 5
    session.add_all(
        TransactionFactory.create_batch(5, user_id=user.id, description='description')
    )
    await session.commit()
    response = client.get(
        '/transactions/?description=desc',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['transactions']) == expected_transactions_desc


@pytest.mark.asyncio
async def test_list_transactions_filters_combined(session, client, user, token):
    expected_transactions_desc_title = 5
    session.add_all(
        TransactionFactory.create_batch(
            5,
            user_id=user.id,
            title='Test combinado',
            description='combina description',
            state='feita',
        )
    )

    session.add_all(
        TransactionFactory.create_batch(
            3, title='Roxos', description='Purples', state='fazendo'
        )
    )
    await session.commit()
    response = client.get(
        '/transactions/?title=Test combinado&description=combina&state=feita',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['transactions']) == expected_transactions_desc_title


def test_patch_transaction_error(client, token):
    response = client.patch(
        '/transactions/10', json={}, headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Not Found'}


@pytest.mark.asyncio
async def test_patch_transaction(session, client, user, token):
    transaction = TransactionFactory(user_id=user.id)

    session.add(transaction)
    await session.commit()

    response = client.patch(
        f'/transactions/{transaction.id}',
        json={
            'title': 'teste!',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['title'] == 'teste!'


def test_delete_error(client, token):
    response = client.delete(
        '/transactions/10',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Not Found'}


@pytest.mark.asyncio
async def test_delete_transaction(session, client, user, token):
    transaction = TransactionFactory(user_id=user.id)
    session.add(transaction)
    await session.commit()

    response = client.delete(
        f'/transactions/{transaction.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Transaction has been delete successfully'}
