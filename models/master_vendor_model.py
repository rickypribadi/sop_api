from sqlmodel import Field

from models.base_model import BaseInstanceModel, SQLModel


class MasterVendorBase(SQLModel):
    kode: str = Field(nullable=False)
    nama: str = Field(nullable=False)


class MasterVendorFullBase(BaseInstanceModel, MasterVendorBase):
    pass


class MasterVendor(MasterVendorFullBase, table=True):
    pass
