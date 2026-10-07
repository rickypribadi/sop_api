from decimal import Decimal
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from models.base_model import BaseInstanceModel, SQLModel

if TYPE_CHECKING:
    from models import MasterBarang, Purchase, PurchaseDetailPlacement


class PurchaseDetailBase(SQLModel):
    purchase_hd_id: str = Field(nullable=False, foreign_key="purchase.id", index=True)
    no_order: int = Field(default=0, nullable=False)
    barang_id: str = Field(nullable=False, foreign_key="master_barang.id")
    jumlah: int = Field(default=0, nullable=False)
    harga_beli: Decimal = Field(default=Decimal(0), max_digits=18, decimal_places=2)
    hpp: Decimal = Field(default=Decimal(0), max_digits=18, decimal_places=2)
    jumlah_placed: int = Field(default=0, nullable=False)  # sudah ditempatkan


class PurchaseDetailFullBase(BaseInstanceModel, PurchaseDetailBase):
    pass


class PurchaseDetail(PurchaseDetailFullBase, table=True):
    purchase: "Purchase" = Relationship(
        back_populates="purchase_dts",
        sa_relationship_kwargs={"lazy": "select"},
    )
    barang: "MasterBarang" = Relationship(sa_relationship_kwargs={"lazy": "select"})
    placement_dts: list["PurchaseDetailPlacement"] = Relationship(
        back_populates="purchase_dt",
        sa_relationship_kwargs={"lazy": "select", "cascade": "all, delete-orphan"},
    )
