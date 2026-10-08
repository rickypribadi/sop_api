from datetime import date
from decimal import Decimal

from sqlmodel import SQLModel

from models.sales_model import SalesFullBase
from models.sales_detail_model import SalesDetailFullBase


class SalesDetailCreateSch(SQLModel):
    barang_id: str
    lokasi_id: str
    jumlah: int
    harga_jual: Decimal


class SalesCreateSch(SQLModel):
    nomor: str
    nama_pelanggan: str | None = None
    tanggal: date | None = None
    diskon: Decimal = Decimal(0)
    pajak: Decimal = Decimal(0)
    rounding: Decimal = Decimal(0)
    remarks: str | None = None
    details: list[SalesDetailCreateSch]


class SalesUpdateSch(SQLModel):
    nomor: str | None = None
    nama_pelanggan: str | None = None
    tanggal: date | None = None
    remarks: str | None = None


class SalesDetailSch(SalesDetailFullBase):
    pass


class SalesSch(SalesFullBase):
    pass


class SalesByIdSch(SalesFullBase):
    sales_dts: list[SalesDetailSch] = []


# Refund penjualan: rusak=True => REFUND_RUSAK (stok tidak bertambah)
class RefundCreateSch(SQLModel):
    sales_dt_id: str
    jumlah: int
    rusak: bool = False


class RefundBatchCreateSch(SQLModel):
    refunds: list[RefundCreateSch]
