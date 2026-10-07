from sqlmodel import Field

from models.base_model import BaseInstanceModel, SQLModel


class MasterLokasiBase(SQLModel):
    nama: str = Field(nullable=False)
    is_active: bool = Field(default=True, nullable=False)


class MasterLokasiFullBase(BaseInstanceModel, MasterLokasiBase):
    pass


class MasterLokasi(MasterLokasiFullBase, table=True):
    pass
