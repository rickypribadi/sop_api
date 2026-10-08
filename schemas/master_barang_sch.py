from decimal import Decimal

from sqlmodel import SQLModel

from models.master_barang_model import MasterBarangBase, MasterBarangFullBase


class MasterBarangCreateSch(SQLModel):
    """Stok (jumlah) & HPP tidak diisi manual; dihitung dari transaksi stok."""

    kode: str
    nama: str
    barcode: str | None = None
    harga_jual: Decimal = Decimal(0)
    is_active: bool = True


class MasterBarangUpdateSch(SQLModel):
    kode: str | None = None
    nama: str | None = None
    barcode: str | None = None
    harga_jual: Decimal | None = None
    is_active: bool | None = None


class MasterBarangSch(MasterBarangFullBase):
    pass


class MasterBarangByIdSch(MasterBarangFullBase):
    pass
