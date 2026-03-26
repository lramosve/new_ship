from app.db import engine, Base
from app import models  # Import all model modules to ensure they're registered
from app.models import Project, Document, User, Issue, Plan

def init_db():
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    init_db()
    print("Database tables created successfully!")
