from decimal import Decimal
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from models.base_model import BaseInstanceModel, SQLModel

if TYPE_CHECKING:
    from models import MasterBarang, MasterLokasi, Sales


class SalesDetailBase(SQLModel):
    sales_id: str = Field(nullable=False, foreign_key="sales.id", index=True)
    no_order: int = Field(default=0, nullable=False)
    barang_id: str = Field(nullable=False, foreign_key="master_barang.id")
    lokasi_id: str = Field(nullable=False, foreign_key="master_lokasi.id")
    jumlah: int = Field(default=0, nullable=False)
    harga_jual: Decimal = Field(default=Decimal(0), max_digits=18, decimal_places=2)
    hpp: Decimal = Field(default=Decimal(0), max_digits=18, decimal_places=2)
    jumlah_refund: int = Field(default=0, nullable=False)


class SalesDetailFullBase(BaseInstanceModel, SalesDetailBase):
    pass


class SalesDetail(SalesDetailFullBase, table=True):
    sales: "Sales" = Relationship(
        back_populates="sales_dts",
        sa_relationship_kwargs={"lazy": "select"},
    )
    barang: "MasterBarang" = Relationship(sa_relationship_kwargs={"lazy": "select"})
    lokasi: "MasterLokasi" = Relationship(sa_relationship_kwargs={"lazy": "select"})
