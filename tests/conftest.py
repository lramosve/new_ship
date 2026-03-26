import os
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set test database URL - use SQLite for testing
os.environ['DATABASE_URL'] = 'sqlite:///./test_ship_db.db'
os.environ['SECRET_KEY'] = 'test-secret-key'

from app.db import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402

# Create a new database engine for testing
engine = create_engine(
    os.environ['DATABASE_URL'],
    connect_args={'check_same_thread': False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope='session', autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope='function')
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


session_override = None


def override_get_db():
    global session_override
    if session_override is not None:
        yield session_override
    else:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope='function')
def client(db_session):
    global session_override
    session_override = db_session
    yield TestClient(app, raise_server_exceptions=False)
    session_override = None


@pytest.fixture(scope='function')
def auth_headers(client):
    create_response = client.post(
        '/users/',
        json={'name': 'Test User', 'email': 'tester@example.com', 'password': 'password123'},
    )
    assert create_response.status_code == 201

    login_response = client.post(
        '/auth/login',
        json={'email': 'tester@example.com', 'password': 'password123'},
    )
    assert login_response.status_code == 200
    token = login_response.json()['access_token']
    return {'Authorization': f'Bearer {token}'}
