from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from models.base_model import BaseInstanceModel, SQLModel

if TYPE_CHECKING:
    from models import MasterBarang, StockOpname


class StockOpnameDetailBase(SQLModel):
    opname_id: str = Field(nullable=False, foreign_key="stock_opname.id", index=True)
    barang_id: str = Field(nullable=False, foreign_key="master_barang.id")
    qty_sistem: int = Field(default=0, nullable=False)
    qty_fisik: int = Field(default=0, nullable=False)
    selisih: int = Field(default=0, nullable=False)


class StockOpnameDetailFullBase(BaseInstanceModel, StockOpnameDetailBase):
    pass


class StockOpnameDetail(StockOpnameDetailFullBase, table=True):
    opname: "StockOpname" = Relationship(
        back_populates="opname_dts",
        sa_relationship_kwargs={"lazy": "select"},
    )
    barang: "MasterBarang" = Relationship(sa_relationship_kwargs={"lazy": "select"})
