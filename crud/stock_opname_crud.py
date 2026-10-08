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
from models.stock_ledger_model import StockLedger
from models.stock_opname_model import StockOpname
from models.stock_opname_detail_model import StockOpnameDetail
from schemas.stock_opname_sch import StockOpnameCreateSch, StockOpnameUpdateSch
from services import stock_service


class CRUDStockOpname(
    CRUDBase[StockOpname, StockOpnameCreateSch, StockOpnameUpdateSch]
):
    async def get_full(self, *, id: str) -> StockOpname | None:
        result = await db.session.execute(
            select(StockOpname)
            .where(StockOpname.id == id)
            .options(selectinload(StockOpname.opname_dts))
        )
        return result.scalar_one_or_none()

    async def create_opname(
        self,
        *,
        sch: StockOpnameCreateSch,
        instance_id: str,
        created_by: str | None = None,
    ) -> StockOpname:
        """Opname: bandingkan qty fisik vs sistem, sesuaikan via ledger OPNAME.

        Selisih positif menambah stok (qty_in), negatif mengurangi (qty_out).
        HPP tidak berubah oleh penyesuaian opname.
        """
        db_session: AsyncSession = db.session

        lokasi = await db_session.get(MasterLokasi, sch.lokasi_id)
        if lokasi is None or lokasi.instance_id != instance_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Lokasi tidak ditemukan")

        try:
            opname = StockOpname(
                instance_id=instance_id,
                nomor=sch.nomor,
                tanggal=sch.tanggal or date.today(),
                lokasi_id=sch.lokasi_id,
                remarks=sch.remarks,
            )
            if created_by:
                opname.created_by = opname.updated_by = created_by
            db_session.add(opname)
            await db_session.flush()

            for d in sch.details:
                barang = await db_session.get(MasterBarang, d.barang_id)
                if barang is None or barang.instance_id != instance_id:
                    raise HTTPException(
                        status.HTTP_404_NOT_FOUND,
                        f"Barang {d.barang_id} tidak ditemukan",
                    )

                qty_sistem = await stock_service.lokasi_saldo(
                    db_session,
                    instance_id=instance_id,
                    barang_id=d.barang_id,
                    lokasi_id=sch.lokasi_id,
                )
                selisih = d.qty_fisik - qty_sistem

                opn_dt = StockOpnameDetail(
                    instance_id=instance_id,
                    opname_id=opname.id,
                    barang_id=d.barang_id,
                    qty_sistem=qty_sistem,
                    qty_fisik=d.qty_fisik,
                    selisih=selisih,
                )
                if created_by:
                    opn_dt.created_by = opn_dt.updated_by = created_by
                db_session.add(opn_dt)

                if selisih != 0:
                    barang.jumlah = barang.jumlah + selisih
                    db_session.add(barang)
                    ledger = StockLedger(
                        instance_id=instance_id,
                        barang_id=barang.id,
                        lokasi_id=sch.lokasi_id,
                        jenis=LedgerTypeEnum.OPNAME,
                        harga=Decimal(barang.hpp),
                        qty_in=selisih if selisih > 0 else 0,
                        qty_out=-selisih if selisih < 0 else 0,
                        saldo_qty=barang.jumlah,
                        hpp=Decimal(barang.hpp),
                        ref_type="opname",
                        ref_id=opname.id,
                    )
                    if created_by:
                        ledger.created_by = ledger.updated_by = created_by
                    db_session.add(ledger)

            await db_session.commit()
            await db_session.refresh(opname)
            return opname
        except HTTPException:
            await db_session.rollback()
            raise
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))


stock_opname = CRUDStockOpname(StockOpname)
