from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=1000)


class ProjectCreate(ProjectBase):
    pass


class ProjectList(BaseModel):
    items: list['Project']
    total: int


class Project(ProjectBase):
    id: int

    model_config = {"from_attributes": True}
