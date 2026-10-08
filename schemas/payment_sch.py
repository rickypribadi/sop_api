from datetime import date
from decimal import Decimal

from sqlmodel import SQLModel

from models.payment_model import PaymentFullBase


class PaymentCreateSch(SQLModel):
    invoice_id: str
    nomor: str
    tanggal: date | None = None
    nama_pembayar: str | None = None
    nama_penerima: str | None = None
    amount: Decimal


class PaymentUpdateSch(SQLModel):
    nomor: str | None = None
    tanggal: date | None = None
    nama_pembayar: str | None = None
    nama_penerima: str | None = None


class PaymentSch(PaymentFullBase):
    pass


class PaymentByIdSch(PaymentFullBase):
    pass
