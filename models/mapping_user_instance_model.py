from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from models.base_model import BaseULIDModel, SQLModel

if TYPE_CHECKING:
    from models import MasterInstance, MasterUser, Role


class MappingUserInstanceBase(SQLModel):
    user_id: str = Field(nullable=False, foreign_key="master_user.id", index=True)
    instance_id: str = Field(
        nullable=False, foreign_key="master_instance.id", index=True
    )
    role_id: str = Field(nullable=False, foreign_key="role.id", index=True)
    is_active: bool = Field(default=True, nullable=False)


class MappingUserInstanceFullBase(BaseULIDModel, MappingUserInstanceBase):
    pass


class MappingUserInstance(MappingUserInstanceFullBase, table=True):
    user: "MasterUser" = Relationship(
        back_populates="instances",
        sa_relationship_kwargs={"lazy": "select"},
    )
    instance: "MasterInstance" = Relationship(
        sa_relationship_kwargs={"lazy": "select"}
    )
    role: "Role" = Relationship(sa_relationship_kwargs={"lazy": "select"})
