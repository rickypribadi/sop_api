from models.base_model import BaseULIDModel
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING
from models.worker_role_model import WorkerRole
from pydantic import field_validator

if  TYPE_CHECKING:
    from models import Role, Department

class WorkerBase(SQLModel):
    name: str | None = Field(nullable=True)
    email: str = Field(nullable=True, unique=True) #email
    is_active: bool = Field(default=True, nullable=False)
    department_id: str = Field(nullable=False, foreign_key='department.id')

    @field_validator('email')
    def validate_code(cls, value):
        return value.lower()

class WorkerFullBase(BaseULIDModel, WorkerBase):
    pass

class Worker(WorkerFullBase, table=True):
    roles: list["Role"] = Relationship(link_model=WorkerRole, sa_relationship_kwargs={"lazy": "select"})
    department: "Department" = Relationship(sa_relationship_kwargs={"lazy": "select"})

    @property
    def department_name(self)-> str | None:
        return getattr(getattr(self, 'department', None), 'name', None)
    @property
    def department_code(self)-> str | None:
        return getattr(getattr(self, 'department', None), 'code', None)