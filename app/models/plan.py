from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.security import utc_now
from app.db import Base


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    week_number = Column(Integer, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Foreign key to Document
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    document = relationship("Document")
