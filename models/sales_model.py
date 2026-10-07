from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from models.base_model import BaseInstanceModel, SQLModel, VoidFieldModel

if TYPE_CHECKING:
    from models import SalesDetail


class SalesBase(SQLModel):
    nomor: str = Field(nullable=False)
    nama_pelanggan: str | None = Field(default=None, nullable=True)
    tanggal: date = Field(default_factory=date.today, nullable=False)
    dpp: Decimal = Field(default=Decimal(0), max_digits=18, decimal_places=2)
    pajak: Decimal = Field(default=Decimal(0), max_digits=18, decimal_places=2)
    diskon: Decimal = Field(default=Decimal(0), max_digits=18, decimal_places=2)
    rounding: Decimal = Field(default=Decimal(0), max_digits=18, decimal_places=2)
    total: Decimal = Field(default=Decimal(0), max_digits=18, decimal_places=2)
    remarks: str | None = Field(default=None, nullable=True)


class SalesFullBase(BaseInstanceModel, VoidFieldModel, SalesBase):
    pass


class Sales(SalesFullBase, table=True):
    sales_dts: list["SalesDetail"] = Relationship(
        back_populates="sales",
        sa_relationship_kwargs={"lazy": "select", "cascade": "all, delete-orphan"},
    )
