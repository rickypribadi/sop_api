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
from models.sales_model import Sales
from models.sales_detail_model import SalesDetail
from schemas.sales_sch import RefundBatchCreateSch, SalesCreateSch, SalesUpdateSch
from services import stock_service


class CRUDSales(CRUDBase[Sales, SalesCreateSch, SalesUpdateSch]):
    async def get_full(self, *, id: str) -> Sales | None:
        result = await db.session.execute(
            select(Sales)
            .where(Sales.id == id)
            .options(selectinload(Sales.sales_dts))
        )
        return result.scalar_one_or_none()

    async def create_sales(
        self,
        *,
        sch: SalesCreateSch,
        instance_id: str,
        created_by: str | None = None,
    ) -> Sales:
        db_session: AsyncSession = db.session

        try:
            sales = Sales(
                instance_id=instance_id,
                nomor=sch.nomor,
                nama_pelanggan=sch.nama_pelanggan,
                tanggal=sch.tanggal or date.today(),
                diskon=sch.diskon,
                pajak=sch.pajak,
                rounding=sch.rounding,
                remarks=sch.remarks,
            )
            if created_by:
                sales.created_by = sales.updated_by = created_by
            db_session.add(sales)
            await db_session.flush()

            dpp = Decimal(0)
            for i, d in enumerate(sch.details, start=1):
                barang = await db_session.get(MasterBarang, d.barang_id)
                if barang is None or barang.instance_id != instance_id:
                    raise HTTPException(
                        status.HTTP_404_NOT_FOUND,
                        f"Barang {d.barang_id} tidak ditemukan",
                    )
                lokasi = await db_session.get(MasterLokasi, d.lokasi_id)
                if lokasi is None or lokasi.instance_id != instance_id:
                    raise HTTPException(
                        status.HTTP_404_NOT_FOUND,
                        f"Lokasi {d.lokasi_id} tidak ditemukan",
                    )

                saldo = await stock_service.lokasi_saldo(
                    db_session,
                    instance_id=instance_id,
                    barang_id=d.barang_id,
                    lokasi_id=d.lokasi_id,
                )
                if d.jumlah > saldo:
                    raise HTTPException(
                        status.HTTP_409_CONFLICT,
                        f"Stok di lokasi tidak cukup untuk {barang.nama}. "
                        f"Tersedia {saldo}, diminta {d.jumlah}.",
                    )

                hpp_saat_jual = Decimal(barang.hpp)
                detail = SalesDetail(
                    instance_id=instance_id,
                    sales_id=sales.id,
                    no_order=i,
                    barang_id=d.barang_id,
                    lokasi_id=d.lokasi_id,
                    jumlah=d.jumlah,
                    harga_jual=d.harga_jual,
                    hpp=hpp_saat_jual,
                )
                if created_by:
                    detail.created_by = detail.updated_by = created_by
                db_session.add(detail)
                await db_session.flush()

                await stock_service.post_movement(
                    db_session,
                    instance_id=instance_id,
                    barang=barang,
                    jenis=LedgerTypeEnum.JUAL,
                    qty=d.jumlah,
                    harga=Decimal(d.harga_jual),
                    lokasi_id=d.lokasi_id,
                    ref_type="sales",
                    ref_id=detail.id,
                    created_by=created_by,
                )
                dpp += Decimal(d.harga_jual) * d.jumlah

            sales.dpp = dpp
            sales.total = (
                dpp
                - Decimal(sch.diskon)
                + Decimal(sch.pajak)
                + Decimal(sch.rounding)
            )
            db_session.add(sales)

            await db_session.commit()
            await db_session.refresh(sales)
            return sales
        except HTTPException:
            await db_session.rollback()
            raise
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

    async def create_refund(
        self,
        *,
        sales_id: str,
        sch: RefundBatchCreateSch,
        instance_id: str,
        created_by: str | None = None,
    ) -> Sales:
        """Refund penjualan: rusak=True -> REFUND_RUSAK (stok tidak bertambah)."""
        db_session: AsyncSession = db.session

        sales = await db_session.get(Sales, sales_id)
        if sales is None or sales.instance_id != instance_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Sales tidak ditemukan")
        if sales.is_void:
            raise HTTPException(status.HTTP_409_CONFLICT, "Sales sudah void")

        try:
            for r in sch.refunds:
                s_dt = await db_session.get(SalesDetail, r.sales_dt_id)
                if s_dt is None or s_dt.sales_id != sales_id:
                    raise HTTPException(
                        status.HTTP_404_NOT_FOUND,
                        f"Detail sales {r.sales_dt_id} tidak ditemukan",
                    )
                sisa_refund = s_dt.jumlah - s_dt.jumlah_refund
                if r.jumlah > sisa_refund:
                    raise HTTPException(
                        status.HTTP_409_CONFLICT,
                        f"Qty refund {r.jumlah} melebihi sisa yang bisa direfund ({sisa_refund})",
                    )

                barang = await db_session.get(MasterBarang, s_dt.barang_id)
                jenis = (
                    LedgerTypeEnum.REFUND_RUSAK if r.rusak else LedgerTypeEnum.REFUND
                )
                await stock_service.post_movement(
                    db_session,
                    instance_id=instance_id,
                    barang=barang,
                    jenis=jenis,
                    qty=r.jumlah,
                    harga=Decimal(s_dt.hpp),
                    lokasi_id=None if r.rusak else s_dt.lokasi_id,
                    ref_type="sales_refund",
                    ref_id=s_dt.id,
                    created_by=created_by,
                )
                s_dt.jumlah_refund += r.jumlah
                db_session.add(s_dt)

            await db_session.commit()
            await db_session.refresh(sales)
            return sales
        except HTTPException:
            await db_session.rollback()
            raise
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))


sales = CRUDSales(Sales)
