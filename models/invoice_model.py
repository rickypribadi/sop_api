from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from models.base_model import BaseInstanceModel, SQLModel, VoidFieldModel

if TYPE_CHECKING:
    from models import InvoiceDetail, Purchase


class InvoiceBase(SQLModel):
    nomor: str = Field(nullable=False)
    purchase_hd_id: str = Field(nullable=False, foreign_key="purchase.id")
    tanggal: date = Field(default_factory=date.today, nullable=False)
    tanggal_jatuh_tempo: date | None = Field(default=None, nullable=True)
    dpp: Decimal = Field(default=Decimal(0), max_digits=18, decimal_places=2)
    diskon: Decimal = Field(default=Decimal(0), max_digits=18, decimal_places=2)
    pph: Decimal = Field(default=Decimal(0), max_digits=18, decimal_places=2)
    ppn: Decimal = Field(default=Decimal(0), max_digits=18, decimal_places=2)
    total: Decimal = Field(default=Decimal(0), max_digits=18, decimal_places=2)


class InvoiceFullBase(BaseInstanceModel, VoidFieldModel, InvoiceBase):
    pass


class Invoice(InvoiceFullBase, table=True):
    purchase: "Purchase" = Relationship(sa_relationship_kwargs={"lazy": "select"})
    invoice_dts: list["InvoiceDetail"] = Relationship(
        back_populates="invoice",
        sa_relationship_kwargs={"lazy": "select", "cascade": "all, delete-orphan"},
    )
