from decimal import Decimal

from pydantic import BaseModel


class LaporanStokItemSch(BaseModel):
    barang_id: str
    kode: str
    nama: str
    jumlah: int
    hpp: Decimal
    nilai_persediaan: Decimal


class LaporanPenjualanItemSch(BaseModel):
    barang_id: str
    kode: str
    nama: str
    qty_terjual: int
    total_penjualan: Decimal
    total_hpp: Decimal
    laba_kotor: Decimal


class LaporanPenjualanBulananSch(BaseModel):
    tahun: int
    bulan: int
    items: list[LaporanPenjualanItemSch]
    total_penjualan: Decimal
    total_hpp: Decimal
    total_laba_kotor: Decimal
