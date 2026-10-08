from datetime import date

from sqlmodel import SQLModel

from models.invoice_model import InvoiceFullBase
from models.invoice_detail_model import InvoiceDetailFullBase


class InvoiceCreateSch(SQLModel):
    nomor: str
    purchase_hd_id: str
    tanggal: date | None = None
    tanggal_jatuh_tempo: date | None = None


class InvoiceUpdateSch(SQLModel):
    nomor: str | None = None
    tanggal: date | None = None
    tanggal_jatuh_tempo: date | None = None


class InvoiceDetailSch(InvoiceDetailFullBase):
    pass


class InvoiceSch(InvoiceFullBase):
    pass


class InvoiceByIdSch(InvoiceFullBase):
    invoice_dts: list[InvoiceDetailSch] = []


# Retur barang invoice (hanya untuk yang sudah ditempatkan ke lokasi)
class ReturCreateSch(SQLModel):
    invoice_dt_id: str
    jumlah: int


class ReturBatchCreateSch(SQLModel):
    returs: list[ReturCreateSch]
