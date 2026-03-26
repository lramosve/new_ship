from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.security import utc_now
from app.db import Base


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    status = Column(String, index=True)
    priority = Column(String, index=True)
    progress = Column(Integer, default=0)
    start_date = Column(Date, nullable=True)
    due_date = Column(Date, nullable=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True, index=True)
    assignee_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    project = relationship('Project')
    assignee = relationship('User')
