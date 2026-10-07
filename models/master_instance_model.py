from sqlmodel import Field

from models.base_model import BaseULIDModel, SQLModel


class MasterInstanceBase(SQLModel):
    kode: str = Field(nullable=False, unique=True)
    nama: str = Field(nullable=False)
    is_active: bool = Field(default=True, nullable=False)


class MasterInstanceFullBase(BaseULIDModel, MasterInstanceBase):
    pass


class MasterInstance(MasterInstanceFullBase, table=True):
    pass
