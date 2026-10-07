from decimal import Decimal

from sqlmodel import Field

from models.base_model import BaseInstanceModel, SQLModel


class MasterBarangBase(SQLModel):
    kode: str = Field(nullable=False)
    nama: str = Field(nullable=False)
    barcode: str | None = Field(default=None, nullable=True)
    jumlah: int = Field(default=0, nullable=False)                 # stok total
    hpp: Decimal = Field(default=Decimal(0), max_digits=18, decimal_places=2)
    harga_jual: Decimal = Field(default=Decimal(0), max_digits=18, decimal_places=2)
    is_active: bool = Field(default=True, nullable=False)


class MasterBarangFullBase(BaseInstanceModel, MasterBarangBase):
    pass


class MasterBarang(MasterBarangFullBase, table=True):
    pass
