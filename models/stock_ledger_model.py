from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from common.enum import LedgerTypeEnum
from models.base_model import BaseInstanceModel, SQLModel

if TYPE_CHECKING:
    from models import MasterBarang, MasterLokasi


class StockLedgerBase(SQLModel):
    """Kartu stok per barang per lokasi, menyimpan jejak HPP moving average."""

    tanggal: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    barang_id: str = Field(nullable=False, foreign_key="master_barang.id", index=True)
    lokasi_id: str | None = Field(
        default=None, foreign_key="master_lokasi.id", index=True
    )
    jenis: LedgerTypeEnum = Field(nullable=False)
    harga: Decimal = Field(default=Decimal(0), max_digits=18, decimal_places=2)
    qty_in: int = Field(default=0, nullable=False)
    qty_out: int = Field(default=0, nullable=False)
    saldo_qty: int = Field(default=0, nullable=False)              # stok sesudah
    hpp: Decimal = Field(default=Decimal(0), max_digits=18, decimal_places=2)  # HPP sesudah
    ref_type: str | None = Field(default=None, nullable=True)
    ref_id: str | None = Field(default=None, nullable=True, max_length=26)


class StockLedgerFullBase(BaseInstanceModel, StockLedgerBase):
    pass


class StockLedger(StockLedgerFullBase, table=True):
    barang: "MasterBarang" = Relationship(sa_relationship_kwargs={"lazy": "select"})
    lokasi: "MasterLokasi" = Relationship(sa_relationship_kwargs={"lazy": "select"})
