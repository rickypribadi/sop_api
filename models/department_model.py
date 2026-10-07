from sqlmodel import Field
from pydantic import field_validator

from models.base_model import BaseULIDModel, SQLModel


class DepartmentBase(SQLModel):
    code: str | None = Field(default=None, nullable=True, unique=True)
    name: str = Field(nullable=False)
    is_active: bool = Field(default=True, nullable=False)

    @field_validator("code")
    def uppercase_code(cls, value):
        return value.upper() if value else value


class DepartmentFullBase(BaseULIDModel, DepartmentBase):
    pass


class Department(DepartmentFullBase, table=True):
    pass
