from datetime import date
from decimal import Decimal

from fastapi import HTTPException, status
from fastapi_async_sqlalchemy import db
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from crud.base_crud import CRUDBase
from models.invoice_model import Invoice
from models.payment_model import Payment
from schemas.payment_sch import PaymentCreateSch, PaymentUpdateSch


class CRUDPayment(CRUDBase[Payment, PaymentCreateSch, PaymentUpdateSch]):
    async def create_payment(
        self,
        *,
        sch: PaymentCreateSch,
        instance_id: str,
        created_by: str | None = None,
    ) -> Payment:
        db_session: AsyncSession = db.session

        invoice = await db_session.get(Invoice, sch.invoice_id)
        if invoice is None or invoice.instance_id != instance_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Invoice tidak ditemukan")
        if invoice.is_void:
            raise HTTPException(status.HTTP_409_CONFLICT, "Invoice sudah void")

        paid = await db_session.execute(
            select(func.coalesce(func.sum(Payment.amount), 0)).where(
                Payment.invoice_id == invoice.id, Payment.is_void == False  # noqa: E712
            )
        )
        sisa = Decimal(invoice.total) - Decimal(paid.scalar_one())
        if Decimal(sch.amount) > sisa:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                f"Pembayaran {sch.amount} melebihi sisa tagihan ({sisa})",
            )

        try:
            payment = Payment(
                instance_id=instance_id,
                invoice_id=invoice.id,
                nomor=sch.nomor,
                tanggal=sch.tanggal or date.today(),
                nama_pembayar=sch.nama_pembayar,
                nama_penerima=sch.nama_penerima,
                amount=sch.amount,
            )
            if created_by:
                payment.created_by = payment.updated_by = created_by
            db_session.add(payment)
            await db_session.commit()
            await db_session.refresh(payment)
            return payment
        except HTTPException:
            await db_session.rollback()
            raise
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))


payment = CRUDPayment(Payment)
