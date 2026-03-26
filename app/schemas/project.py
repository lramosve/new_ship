from pydantic import BaseModel

class ProjectBase(BaseModel):
    name: str
    description: str

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int

    class ConfigDict:
        from_attributes = True