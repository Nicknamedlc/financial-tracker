from http import HTTPStatus

from jwt import decode

from app.controllers.security import create_access_token


def test_jwt(token, settings):
    data = {'test': 'test'}
    token = create_access_token(data)

    decoded = decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)

    assert decoded['test'] == data['test']
    assert 'exp' in decoded


def test_current_no_sub(client, token):
    data = {'no-email': 'test'}
    token = create_access_token(data)

    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_current_no_user(client, token):
    data = {'sub': 'test@example.com'}
    token = create_access_token(data)

    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
