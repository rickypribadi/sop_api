from datetime import date
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from models.base_model import BaseInstanceModel, SQLModel, VoidFieldModel

if TYPE_CHECKING:
    from models import MasterLokasi, StockOpnameDetail


class StockOpnameBase(SQLModel):
    nomor: str = Field(nullable=False)
    tanggal: date = Field(default_factory=date.today, nullable=False)
    lokasi_id: str = Field(nullable=False, foreign_key="master_lokasi.id")
    remarks: str | None = Field(default=None, nullable=True)


class StockOpnameFullBase(BaseInstanceModel, VoidFieldModel, StockOpnameBase):
    pass


class StockOpname(StockOpnameFullBase, table=True):
    lokasi: "MasterLokasi" = Relationship(sa_relationship_kwargs={"lazy": "select"})
    opname_dts: list["StockOpnameDetail"] = Relationship(
        back_populates="opname",
        sa_relationship_kwargs={"lazy": "select", "cascade": "all, delete-orphan"},
    )
