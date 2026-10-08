from datetime import date
from decimal import Decimal

from fastapi import HTTPException, status
from fastapi_async_sqlalchemy import db
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from common.enum import LedgerTypeEnum
from crud.base_crud import CRUDBase
from models.master_barang_model import MasterBarang
from models.master_lokasi_model import MasterLokasi
from models.master_vendor_model import MasterVendor
from models.purchase_model import Purchase
from models.purchase_detail_model import PurchaseDetail
from models.purchase_detail_placement_model import PurchaseDetailPlacement
from schemas.purchase_sch import (
    PlacementBatchCreateSch,
    PurchaseCreateSch,
    PurchaseUpdateSch,
)
from services import stock_service


class CRUDPurchase(CRUDBase[Purchase, PurchaseCreateSch, PurchaseUpdateSch]):
    async def get_full(self, *, id: str) -> Purchase | None:
        """Ambil purchase + detail (eager-load untuk response ByIdSch)."""
        result = await db.session.execute(
            select(Purchase)
            .where(Purchase.id == id)
            .options(selectinload(Purchase.purchase_dts))
        )
        return result.scalar_one_or_none()

    async def create_purchase(
        self,
        *,
        sch: PurchaseCreateSch,
        instance_id: str,
        created_by: str | None = None,
    ) -> Purchase:
        db_session: AsyncSession = db.session

        vendor = await db_session.get(MasterVendor, sch.vendor_id)
        if vendor is None or vendor.instance_id != instance_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Vendor tidak ditemukan")

        try:
            purchase = Purchase(
                instance_id=instance_id,
                nomor=sch.nomor,
                tanggal=sch.tanggal or date.today(),
                vendor_id=sch.vendor_id,
                diskon=sch.diskon,
                pph=sch.pph,
                ppn=sch.ppn,
                remarks=sch.remarks,
            )
            if created_by:
                purchase.created_by = purchase.updated_by = created_by
            db_session.add(purchase)
            await db_session.flush()

            dpp = Decimal(0)
            for i, d in enumerate(sch.details, start=1):
                barang = await db_session.get(MasterBarang, d.barang_id)
                if barang is None or barang.instance_id != instance_id:
                    raise HTTPException(
                        status.HTTP_404_NOT_FOUND,
                        f"Barang {d.barang_id} tidak ditemukan",
                    )
                dpp += Decimal(d.harga_beli) * d.jumlah
                detail = PurchaseDetail(
                    instance_id=instance_id,
                    purchase_hd_id=purchase.id,
                    no_order=i,
                    barang_id=d.barang_id,
                    jumlah=d.jumlah,
                    harga_beli=d.harga_beli,
                    hpp=d.harga_beli,
                )
                if created_by:
                    detail.created_by = detail.updated_by = created_by
                db_session.add(detail)

            purchase.dpp = dpp
            purchase.total = (
                dpp - Decimal(sch.diskon) - Decimal(sch.pph) + Decimal(sch.ppn)
            )
            db_session.add(purchase)

            await db_session.commit()
            await db_session.refresh(purchase)
            return purchase
        except HTTPException:
            await db_session.rollback()
            raise
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

    async def create_placement(
        self,
        *,
        purchase_id: str,
        sch: PlacementBatchCreateSch,
        instance_id: str,
        created_by: str | None = None,
    ) -> list[PurchaseDetailPlacement]:
        """Peletakan barang ke lokasi -> ledger MASUK (HPP terhitung)."""
        db_session: AsyncSession = db.session

        purchase = await db_session.get(Purchase, purchase_id)
        if purchase is None or purchase.instance_id != instance_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Purchase tidak ditemukan")
        if purchase.is_void:
            raise HTTPException(status.HTTP_409_CONFLICT, "Purchase sudah void")

        try:
            result: list[PurchaseDetailPlacement] = []
            for p in sch.placements:
                detail = await db_session.get(PurchaseDetail, p.purchase_dt_id)
                if detail is None or detail.purchase_hd_id != purchase_id:
                    raise HTTPException(
                        status.HTTP_404_NOT_FOUND,
                        f"Detail pembelian {p.purchase_dt_id} tidak ditemukan",
                    )
                lokasi = await db_session.get(MasterLokasi, p.lokasi_id)
                if lokasi is None or lokasi.instance_id != instance_id:
                    raise HTTPException(
                        status.HTTP_404_NOT_FOUND,
                        f"Lokasi {p.lokasi_id} tidak ditemukan",
                    )

                sisa = detail.jumlah - detail.jumlah_placed
                if p.jumlah > sisa:
                    raise HTTPException(
                        status.HTTP_409_CONFLICT,
                        f"Qty penempatan {p.jumlah} melebihi sisa belum ditempatkan ({sisa})",
                    )

                placement = PurchaseDetailPlacement(
                    instance_id=instance_id,
                    purchase_dt_id=detail.id,
                    lokasi_id=p.lokasi_id,
                    jumlah=p.jumlah,
                )
                if created_by:
                    placement.created_by = placement.updated_by = created_by
                db_session.add(placement)
                detail.jumlah_placed += p.jumlah
                db_session.add(detail)

                barang = await db_session.get(MasterBarang, detail.barang_id)
                await stock_service.post_movement(
                    db_session,
                    instance_id=instance_id,
                    barang=barang,
                    jenis=LedgerTypeEnum.MASUK,
                    qty=p.jumlah,
                    harga=Decimal(detail.harga_beli),
                    lokasi_id=p.lokasi_id,
                    ref_type="placement",
                    ref_id=placement.id,
                    created_by=created_by,
                )
                result.append(placement)

            await db_session.commit()
            for r in result:
                await db_session.refresh(r)
            return result
        except HTTPException:
            await db_session.rollback()
            raise
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))


purchase = CRUDPurchase(Purchase)
