from app.models.user import User


def test_create_user_hashes_password(client, db_session):
    response = client.post(
        '/users/',
        json={'name': 'Ada Lovelace', 'email': 'ada@example.com', 'password': 'password123'},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload['name'] == 'Ada Lovelace'
    assert payload['email'] == 'ada@example.com'
    assert 'password' not in payload

    user = db_session.query(User).filter(User.email == 'ada@example.com').first()
    assert user is not None
    assert user.hashed_password != 'password123'
    assert len(user.hashed_password) == 64



def test_login_returns_token(client):
    client.post('/users/', json={'name': 'Ada Lovelace', 'email': 'ada@example.com', 'password': 'password123'})
    response = client.post('/auth/login', json={'email': 'ada@example.com', 'password': 'password123'})
    assert response.status_code == 200
    assert 'access_token' in response.json()


def test_current_user_returns_authenticated_identity(client):
    client.post('/users/', json={'name': 'Ada Lovelace', 'email': 'ada@example.com', 'password': 'password123'})
    login_response = client.post('/auth/login', json={'email': 'ada@example.com', 'password': 'password123'})
    token = login_response.json()['access_token']

    me_response = client.get('/users/me', headers={'Authorization': f'Bearer {token}'})

    assert me_response.status_code == 200
    assert me_response.json()['email'] == 'ada@example.com'


def test_create_user_rejects_duplicate_email(client):
    first = client.post(
        '/users/',
        json={'name': 'Ada Lovelace', 'email': 'ada@example.com', 'password': 'password123'},
    )
    assert first.status_code == 201

    second = client.post(
        '/users/',
        json={'name': 'Grace Hopper', 'email': 'ada@example.com', 'password': 'password456'},
    )
    assert second.status_code == 400
    assert second.json()['detail'] == 'A user with that email already exists'



def test_update_user_can_change_password(client, db_session, auth_headers):
    created = client.post(
        '/users/',
        json={'name': 'Ada Lovelace', 'email': 'ada@example.com', 'password': 'password123'},
    )
    user_id = created.json()['id']
    original_hash = db_session.query(User).filter(User.id == user_id).first().hashed_password

    updated = client.put(
        f'/users/{user_id}',
        json={'name': 'Ada Byron', 'email': 'ada.byron@example.com', 'password': 'betterpass123'},
        headers=auth_headers,
    )

    assert updated.status_code == 200
    assert updated.json()['name'] == 'Ada Byron'
    assert updated.json()['email'] == 'ada.byron@example.com'

    refreshed = db_session.query(User).filter(User.id == user_id).first()
    assert refreshed.hashed_password != original_hash



def test_update_user_without_password_preserves_hash(client, db_session, auth_headers):
    created = client.post(
        '/users/',
        json={'name': 'Ada Lovelace', 'email': 'ada@example.com', 'password': 'password123'},
    )
    user_id = created.json()['id']
    original_hash = db_session.query(User).filter(User.id == user_id).first().hashed_password

    updated = client.put(
        f'/users/{user_id}',
        json={'name': 'Ada Byron', 'email': 'ada.byron@example.com'},
        headers=auth_headers,
    )

    assert updated.status_code == 200
    refreshed = db_session.query(User).filter(User.id == user_id).first()
    assert refreshed.hashed_password == original_hash
