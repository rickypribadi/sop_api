from datetime import date
from decimal import Decimal

from fastapi import HTTPException, status
from fastapi_async_sqlalchemy import db
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from common.enum import LedgerTypeEnum
from crud.base_crud import CRUDBase
from models.invoice_model import Invoice
from models.invoice_detail_model import InvoiceDetail
from models.master_barang_model import MasterBarang
from models.purchase_model import Purchase
from models.purchase_detail_model import PurchaseDetail
from schemas.invoice_sch import InvoiceCreateSch, InvoiceUpdateSch, ReturBatchCreateSch
from services import stock_service


class CRUDInvoice(CRUDBase[Invoice, InvoiceCreateSch, InvoiceUpdateSch]):
    async def get_full(self, *, id: str) -> Invoice | None:
        result = await db.session.execute(
            select(Invoice)
            .where(Invoice.id == id)
            .options(selectinload(Invoice.invoice_dts))
        )
        return result.scalar_one_or_none()

    async def create_invoice(
        self,
        *,
        sch: InvoiceCreateSch,
        instance_id: str,
        created_by: str | None = None,
    ) -> Invoice:
        db_session: AsyncSession = db.session

        purchase = await db_session.get(Purchase, sch.purchase_hd_id)
        if purchase is None or purchase.instance_id != instance_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Purchase tidak ditemukan")
        if purchase.is_void:
            raise HTTPException(status.HTTP_409_CONFLICT, "Purchase sudah void")

        existing = await db_session.execute(
            select(Invoice).where(
                Invoice.purchase_hd_id == purchase.id, Invoice.is_void == False  # noqa: E712
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status.HTTP_409_CONFLICT, "Invoice untuk purchase ini sudah ada"
            )

        try:
            invoice = Invoice(
                instance_id=instance_id,
                nomor=sch.nomor,
                purchase_hd_id=purchase.id,
                tanggal=sch.tanggal or date.today(),
                tanggal_jatuh_tempo=sch.tanggal_jatuh_tempo,
                dpp=purchase.dpp,
                diskon=purchase.diskon,
                pph=purchase.pph,
                ppn=purchase.ppn,
                total=purchase.total,
            )
            if created_by:
                invoice.created_by = invoice.updated_by = created_by
            db_session.add(invoice)
            await db_session.flush()

            details = await db_session.execute(
                select(PurchaseDetail).where(
                    PurchaseDetail.purchase_hd_id == purchase.id
                )
            )
            for i, pdt in enumerate(details.scalars().all(), start=1):
                inv_dt = InvoiceDetail(
                    instance_id=instance_id,
                    invoice_id=invoice.id,
                    no_order=i,
                    purchase_dt_id=pdt.id,
                    jumlah=pdt.jumlah,
                    harga=pdt.harga_beli,
                )
                if created_by:
                    inv_dt.created_by = inv_dt.updated_by = created_by
                db_session.add(inv_dt)

            await db_session.commit()
            await db_session.refresh(invoice)
            return invoice
        except HTTPException:
            await db_session.rollback()
            raise
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

    async def create_retur(
        self,
        *,
        invoice_id: str,
        sch: ReturBatchCreateSch,
        instance_id: str,
        created_by: str | None = None,
    ) -> Invoice:
        """Retur barang invoice (hanya untuk barang yang sudah ditempatkan)."""
        db_session: AsyncSession = db.session

        invoice = await db_session.get(Invoice, invoice_id)
        if invoice is None or invoice.instance_id != instance_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Invoice tidak ditemukan")
        if invoice.is_void:
            raise HTTPException(status.HTTP_409_CONFLICT, "Invoice sudah void")

        try:
            for r in sch.returs:
                inv_dt = await db_session.get(InvoiceDetail, r.invoice_dt_id)
                if inv_dt is None or inv_dt.invoice_id != invoice_id:
                    raise HTTPException(
                        status.HTTP_404_NOT_FOUND,
                        f"Detail invoice {r.invoice_dt_id} tidak ditemukan",
                    )

                pdt = await db_session.get(PurchaseDetail, inv_dt.purchase_dt_id)
                if r.jumlah > pdt.jumlah_placed:
                    raise HTTPException(
                        status.HTTP_409_CONFLICT,
                        "Retur hanya untuk barang yang sudah dimasukkan ke lokasi. "
                        f"Sudah ditempatkan {pdt.jumlah_placed}, retur {r.jumlah}.",
                    )
                sisa_retur = inv_dt.jumlah - inv_dt.jumlah_retur
                if r.jumlah > sisa_retur:
                    raise HTTPException(
                        status.HTTP_409_CONFLICT,
                        f"Qty retur {r.jumlah} melebihi sisa yang bisa diretur ({sisa_retur})",
                    )

                barang = await db_session.get(MasterBarang, pdt.barang_id)
                await stock_service.post_movement(
                    db_session,
                    instance_id=instance_id,
                    barang=barang,
                    jenis=LedgerTypeEnum.RETUR,
                    qty=r.jumlah,
                    harga=Decimal(barang.hpp),
                    lokasi_id=None,
                    ref_type="invoice_retur",
                    ref_id=inv_dt.id,
                    created_by=created_by,
                )
                inv_dt.jumlah_retur += r.jumlah
                pdt.jumlah_placed -= r.jumlah
                db_session.add(inv_dt)
                db_session.add(pdt)

            await db_session.commit()
            await db_session.refresh(invoice)
            return invoice
        except HTTPException:
            await db_session.rollback()
            raise
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))


invoice = CRUDInvoice(Invoice)
