from sqlmodel import Field

from models.base_model import BaseULIDModel, SQLModel


class MappingUserInstanceBase(SQLModel):
    user_id: str = Field(nullable=False, foreign_key="master_user.id", index=True)
    instance_id: str = Field(
        nullable=False, foreign_key="master_instance.id", index=True
    )
    is_active: bool = Field(default=True, nullable=False)


class MappingUserInstanceFullBase(BaseULIDModel, MappingUserInstanceBase):
    pass


class MappingUserInstance(MappingUserInstanceFullBase, table=True):
    pass
