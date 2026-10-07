from decimal import Decimal
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from models.base_model import BaseInstanceModel, SQLModel

if TYPE_CHECKING:
    from models import Invoice, PurchaseDetail


class InvoiceDetailBase(SQLModel):
    invoice_id: str = Field(nullable=False, foreign_key="invoice.id", index=True)
    no_order: int = Field(default=0, nullable=False)
    purchase_dt_id: str = Field(nullable=False, foreign_key="purchase_detail.id")
    jumlah: int = Field(default=0, nullable=False)
    harga: Decimal = Field(default=Decimal(0), max_digits=18, decimal_places=2)
    jumlah_retur: int = Field(default=0, nullable=False)


class InvoiceDetailFullBase(BaseInstanceModel, InvoiceDetailBase):
    pass


class InvoiceDetail(InvoiceDetailFullBase, table=True):
    invoice: "Invoice" = Relationship(
        back_populates="invoice_dts",
        sa_relationship_kwargs={"lazy": "select"},
    )
    purchase_dt: "PurchaseDetail" = Relationship(
        sa_relationship_kwargs={"lazy": "select"}
    )
