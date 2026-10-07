from sqlmodel import Field, Relationship
from typing import TYPE_CHECKING

from models.base_model import BaseULIDModel, SQLModel

if TYPE_CHECKING:
    from models import MappingUserInstance


class MasterUserBase(SQLModel):
    nama: str = Field(nullable=False)
    username: str = Field(nullable=False, unique=True)
    password: str = Field(nullable=False)
    is_active: bool = Field(default=True, nullable=False)


class MasterUserFullBase(BaseULIDModel, MasterUserBase):
    pass


class MasterUser(MasterUserFullBase, table=True):
    instances: list["MappingUserInstance"] = Relationship(
        sa_relationship_kwargs={"lazy": "select", "cascade": "all, delete-orphan"}
    )
