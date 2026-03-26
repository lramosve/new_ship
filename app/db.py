from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base as orm_declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Load environment variables - use SQLite unless a non-placeholder DATABASE_URL is supplied.
raw_database_url = os.getenv('DATABASE_URL', '').strip()
if not raw_database_url or 'your_username' in raw_database_url or 'your_password' in raw_database_url:
    DATABASE_URL = 'sqlite:///./ship_db.db'
else:
    DATABASE_URL = raw_database_url

# Create the engine - add special handling for SQLite
engine_kwargs = {}
if DATABASE_URL.startswith('sqlite'):
    engine_kwargs['connect_args'] = {'check_same_thread': False}
engine = create_engine(DATABASE_URL, **engine_kwargs)

# Create the session local class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = orm_declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
