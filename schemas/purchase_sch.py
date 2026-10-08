from datetime import date
from decimal import Decimal

from sqlmodel import SQLModel

from models.purchase_model import PurchaseFullBase
from models.purchase_detail_model import PurchaseDetailFullBase
from models.purchase_detail_placement_model import PurchaseDetailPlacementFullBase


# ---------------------------------------------------------------------------
# Purchase create (header + lines)
# ---------------------------------------------------------------------------
class PurchaseDetailCreateSch(SQLModel):
    barang_id: str
    jumlah: int
    harga_beli: Decimal


class PurchaseCreateSch(SQLModel):
    nomor: str
    tanggal: date | None = None
    vendor_id: str
    diskon: Decimal = Decimal(0)
    pph: Decimal = Decimal(0)
    ppn: Decimal = Decimal(0)
    remarks: str | None = None
    details: list[PurchaseDetailCreateSch]


class PurchaseUpdateSch(SQLModel):
    nomor: str | None = None
    tanggal: date | None = None
    remarks: str | None = None


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------
class PurchaseDetailSch(PurchaseDetailFullBase):
    pass


class PurchaseSch(PurchaseFullBase):
    pass


class PurchaseByIdSch(PurchaseFullBase):
    purchase_dts: list[PurchaseDetailSch] = []


# ---------------------------------------------------------------------------
# Placement (peletakan barang ke lokasi)
# ---------------------------------------------------------------------------
class PlacementCreateSch(SQLModel):
    purchase_dt_id: str
    lokasi_id: str
    jumlah: int


class PlacementBatchCreateSch(SQLModel):
    placements: list[PlacementCreateSch]


class PlacementSch(PurchaseDetailPlacementFullBase):
    pass
