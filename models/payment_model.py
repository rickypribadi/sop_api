from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from models.base_model import BaseInstanceModel, SQLModel, VoidFieldModel

if TYPE_CHECKING:
    from models import Invoice


class PaymentBase(SQLModel):
    invoice_id: str = Field(nullable=False, foreign_key="invoice.id", index=True)
    nomor: str = Field(nullable=False)
    tanggal: date = Field(default_factory=date.today, nullable=False)
    nama_pembayar: str | None = Field(default=None, nullable=True)
    nama_penerima: str | None = Field(default=None, nullable=True)
    amount: Decimal = Field(default=Decimal(0), max_digits=18, decimal_places=2)


class PaymentFullBase(BaseInstanceModel, VoidFieldModel, PaymentBase):
    pass


class Payment(PaymentFullBase, table=True):
    invoice: "Invoice" = Relationship(sa_relationship_kwargs={"lazy": "select"})
