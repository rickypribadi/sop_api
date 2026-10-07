from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from models.base_model import BaseInstanceModel, SQLModel, VoidFieldModel

if TYPE_CHECKING:
    from models import PurchaseDetail


class PurchaseBase(SQLModel):
    nomor: str = Field(nullable=False)
    tanggal: date = Field(default_factory=date.today, nullable=False)
    vendor_id: str = Field(nullable=False, foreign_key="master_vendor.id")
    dpp: Decimal = Field(default=Decimal(0), max_digits=18, decimal_places=2)
    diskon: Decimal = Field(default=Decimal(0), max_digits=18, decimal_places=2)
    pph: Decimal = Field(default=Decimal(0), max_digits=18, decimal_places=2)
    ppn: Decimal = Field(default=Decimal(0), max_digits=18, decimal_places=2)
    total: Decimal = Field(default=Decimal(0), max_digits=18, decimal_places=2)
    remarks: str | None = Field(default=None, nullable=True)


class PurchaseFullBase(BaseInstanceModel, VoidFieldModel, PurchaseBase):
    pass


class Purchase(PurchaseFullBase, table=True):
    purchase_dts: list["PurchaseDetail"] = Relationship(
        back_populates="purchase",
        sa_relationship_kwargs={"lazy": "select", "cascade": "all, delete-orphan"},
    )
