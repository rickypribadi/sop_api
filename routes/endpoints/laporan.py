import calendar
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Header, Query
from fastapi_async_sqlalchemy import db
from sqlmodel import func, select

from models.master_barang_model import MasterBarang
from models.sales_model import Sales
from models.sales_detail_model import SalesDetail
from schemas.laporan_sch import (
    LaporanPenjualanBulananSch,
    LaporanPenjualanItemSch,
    LaporanStokItemSch,
)
from schemas.response_sch import GetResponseBaseSch, create_response

router = APIRouter()


@router.get(
    "/stok", response_model=GetResponseBaseSch[list[LaporanStokItemSch]]
)
async def laporan_stok(x_instance_id: str = Header(..., alias="X-Instance-Id")):
    """Laporan stok: posisi stok & nilai persediaan (qty x HPP) per barang."""
    rows = await db.session.execute(
        select(MasterBarang).where(MasterBarang.instance_id == x_instance_id)
    )
    items = [
        LaporanStokItemSch(
            barang_id=b.id,
            kode=b.kode,
            nama=b.nama,
            jumlah=b.jumlah,
            hpp=Decimal(b.hpp),
            nilai_persediaan=Decimal(b.hpp) * b.jumlah,
        )
        for b in rows.scalars().all()
    ]
    return create_response(data=items)


@router.get(
    "/penjualan-bulanan",
    response_model=GetResponseBaseSch[LaporanPenjualanBulananSch],
)
async def laporan_penjualan_bulanan(
    tahun: int = Query(..., ge=2000, le=2100),
    bulan: int = Query(..., ge=1, le=12),
    x_instance_id: str = Header(..., alias="X-Instance-Id"),
):
    """Laporan penjualan bulanan: qty, omzet, HPP, laba kotor per barang (bersih refund)."""
    last_day = calendar.monthrange(tahun, bulan)[1]
    awal = date(tahun, bulan, 1)
    akhir = date(tahun, bulan, last_day)

    qty_net = SalesDetail.jumlah - SalesDetail.jumlah_refund
    rows = await db.session.execute(
        select(
            SalesDetail.barang_id,
            MasterBarang.kode,
            MasterBarang.nama,
            func.sum(qty_net).label("qty"),
            func.sum(qty_net * SalesDetail.harga_jual).label("omzet"),
            func.sum(qty_net * SalesDetail.hpp).label("hpp"),
        )
        .join(Sales, Sales.id == SalesDetail.sales_id)
        .join(MasterBarang, MasterBarang.id == SalesDetail.barang_id)
        .where(
            Sales.instance_id == x_instance_id,
            Sales.is_void == False,  # noqa: E712
            Sales.tanggal >= awal,
            Sales.tanggal <= akhir,
        )
        .group_by(SalesDetail.barang_id, MasterBarang.kode, MasterBarang.nama)
    )

    items: list[LaporanPenjualanItemSch] = []
    total_jual = Decimal(0)
    total_hpp = Decimal(0)
    for r in rows.all():
        omzet = Decimal(r.omzet or 0)
        hpp = Decimal(r.hpp or 0)
        items.append(
            LaporanPenjualanItemSch(
                barang_id=r.barang_id,
                kode=r.kode,
                nama=r.nama,
                qty_terjual=int(r.qty or 0),
                total_penjualan=omzet,
                total_hpp=hpp,
                laba_kotor=omzet - hpp,
            )
        )
        total_jual += omzet
        total_hpp += hpp

    data = LaporanPenjualanBulananSch(
        tahun=tahun,
        bulan=bulan,
        items=items,
        total_penjualan=total_jual,
        total_hpp=total_hpp,
        total_laba_kotor=total_jual - total_hpp,
    )
    return create_response(data=data)
