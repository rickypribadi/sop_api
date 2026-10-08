from datetime import date

from sqlmodel import SQLModel

from models.stock_opname_model import StockOpnameFullBase
from models.stock_opname_detail_model import StockOpnameDetailFullBase


class OpnameDetailCreateSch(SQLModel):
    barang_id: str
    qty_fisik: int


class StockOpnameCreateSch(SQLModel):
    nomor: str
    tanggal: date | None = None
    lokasi_id: str
    remarks: str | None = None
    details: list[OpnameDetailCreateSch]


class StockOpnameUpdateSch(SQLModel):
    nomor: str | None = None
    tanggal: date | None = None
    remarks: str | None = None


class StockOpnameDetailSch(StockOpnameDetailFullBase):
    pass


class StockOpnameSch(StockOpnameFullBase):
    pass


class StockOpnameByIdSch(StockOpnameFullBase):
    opname_dts: list[StockOpnameDetailSch] = []
