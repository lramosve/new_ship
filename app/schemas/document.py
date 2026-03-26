from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from app.models.document import Document


class DocumentBase(BaseModel):
    title: str
    type: str
    content: Optional[str]


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(DocumentBase):
    pass


class DocumentInDBBase(DocumentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class ConfigDict:
        from_attributes = True


class Document(DocumentInDBBase):
    pass
