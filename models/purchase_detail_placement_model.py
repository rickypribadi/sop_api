from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from models.base_model import BaseInstanceModel, SQLModel

if TYPE_CHECKING:
    from models import MasterLokasi, PurchaseDetail


class PurchaseDetailPlacementBase(SQLModel):
    purchase_dt_id: str = Field(
        nullable=False, foreign_key="purchase_detail.id", index=True
    )
    lokasi_id: str = Field(nullable=False, foreign_key="master_lokasi.id")
    jumlah: int = Field(default=0, nullable=False)


class PurchaseDetailPlacementFullBase(BaseInstanceModel, PurchaseDetailPlacementBase):
    pass


class PurchaseDetailPlacement(PurchaseDetailPlacementFullBase, table=True):
    purchase_dt: "PurchaseDetail" = Relationship(
        back_populates="placement_dts",
        sa_relationship_kwargs={"lazy": "select"},
    )
    lokasi: "MasterLokasi" = Relationship(sa_relationship_kwargs={"lazy": "select"})
