from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


DocumentType = Literal['markdown', 'spec', 'note', 'report']


class DocumentBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    type: DocumentType
    content: str | None = Field(default=None, max_length=5000)


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(DocumentBase):
    pass


class DocumentList(BaseModel):
    items: list['Document']
    total: int


class DocumentInDBBase(DocumentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class ConfigDict:
        from_attributes = True


class Document(DocumentInDBBase):
    pass
