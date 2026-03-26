import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from app.db import Base, get_db
from app.main import app
from fastapi.testclient import TestClient
import os

# Set test database URL - use SQLite for testing
os.environ['DATABASE_URL'] = 'sqlite:///./test_ship_db.db'

# Create a new database engine for testing
engine = create_engine(
    os.environ['DATABASE_URL'],
    connect_args={'check_same_thread': False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope='session', autouse=True)
def setup_database():
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop the database tables after the tests run
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

# Dependency override - create a session that persists within a test function
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