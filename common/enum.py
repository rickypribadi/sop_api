from enum import Enum


class OrderEnumSch(str, Enum):
    ascendent = "ascendent"
    descendent = "descendent"


class LedgerTypeEnum(str, Enum):
    """Jenis pergerakan stok pada kartu stok (stock ledger)."""

    BEGBAL = "BEGBAL"              # saldo awal
    MASUK = "MASUK"               # pembelian / placement masuk ke lokasi
    JUAL = "JUAL"                 # penjualan (stok keluar)
    RETUR = "RETUR"               # retur invoice (stok keluar lagi)
    REFUND = "REFUND"             # refund penjualan biasa (barang masuk kembali)
    REFUND_RUSAK = "REFUND_RUSAK"  # refund barang rusak (stok TIDAK bertambah)
    OPNAME = "OPNAME"             # penyesuaian stok opname
