"""Service stok & HPP (moving average).

Metode HPP: Weighted / Moving Average. Hanya transaksi MASUK/BEGBAL dengan
harga beli baru yang mengubah nilai HPP barang. Transaksi keluar (JUAL, RETUR)
dan masuk-kembali (REFUND biasa) memakai HPP berjalan dan TIDAK mengubahnya.
REFUND_RUSAK tidak menambah stok. OPNAME menyesuaikan stok, HPP tetap.

Mengacu pada sheet "Contoh perhitungan HPP":
    BEGBAL 0            -> saldo 0,  hpp 0
    MASUK  5 @60000     -> saldo 5,  hpp 60000
    JUAL   2 @70000     -> saldo 3,  hpp 60000  (tetap)
    MASUK  10 @65000    -> saldo 13, hpp = (3*60000 + 10*65000)/13
    REFUND_RUSAK 1      -> saldo tetap (stok tidak bertambah)
    REFUND 1            -> saldo +1   (hpp tetap)
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from fastapi import HTTPException, status
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from common.enum import LedgerTypeEnum
from models.master_barang_model import MasterBarang
from models.stock_ledger_model import StockLedger

_CENTS = Decimal("0.01")

_INBOUND = {LedgerTypeEnum.BEGBAL, LedgerTypeEnum.MASUK, LedgerTypeEnum.REFUND}
_OUTBOUND = {LedgerTypeEnum.JUAL, LedgerTypeEnum.RETUR}


def _round(value: Decimal) -> Decimal:
    return Decimal(value).quantize(_CENTS, rounding=ROUND_HALF_UP)


async def lokasi_saldo(
    db_session: AsyncSession,
    *,
    instance_id: str,
    barang_id: str,
    lokasi_id: str,
) -> int:
    """Stok tersedia pada satu lokasi (dihitung dari kartu stok)."""
    total_in = await db_session.execute(
        select(func.coalesce(func.sum(StockLedger.qty_in), 0)).where(
            StockLedger.instance_id == instance_id,
            StockLedger.barang_id == barang_id,
            StockLedger.lokasi_id == lokasi_id,
        )
    )
    total_out = await db_session.execute(
        select(func.coalesce(func.sum(StockLedger.qty_out), 0)).where(
            StockLedger.instance_id == instance_id,
            StockLedger.barang_id == barang_id,
            StockLedger.lokasi_id == lokasi_id,
        )
    )
    return int(total_in.scalar_one()) - int(total_out.scalar_one())


async def post_movement(
    db_session: AsyncSession,
    *,
    instance_id: str,
    barang: MasterBarang,
    jenis: LedgerTypeEnum,
    qty: int,
    harga: Decimal,
    lokasi_id: str | None = None,
    ref_type: str | None = None,
    ref_id: str | None = None,
    created_by: str | None = None,
) -> StockLedger:
    """Catat satu pergerakan stok dan perbarui HPP moving average barang.

    Memperbarui `barang.jumlah` (stok total) dan `barang.hpp` (HPP berjalan),
    lalu menambahkan baris StockLedger ke session (tanpa commit).
    """
    if qty <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Qty harus lebih besar dari 0",
        )

    saldo_lama = int(barang.jumlah)
    hpp_lama = Decimal(barang.hpp)

    qty_in = 0
    qty_out = 0
    hpp_baru = hpp_lama
    saldo_baru = saldo_lama

    if jenis in (LedgerTypeEnum.MASUK, LedgerTypeEnum.BEGBAL):
        qty_in = qty
        saldo_baru = saldo_lama + qty
        if saldo_baru > 0:
            total_nilai = hpp_lama * saldo_lama + Decimal(harga) * qty
            hpp_baru = _round(total_nilai / saldo_baru)
        else:
            hpp_baru = Decimal(0)

    elif jenis == LedgerTypeEnum.REFUND:
        qty_in = qty
        saldo_baru = saldo_lama + qty

    elif jenis == LedgerTypeEnum.REFUND_RUSAK:
        # Barang rusak: tidak menambah stok, tidak mengubah HPP.
        saldo_baru = saldo_lama

    elif jenis in _OUTBOUND:
        if qty > saldo_lama:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Stok tidak cukup untuk {jenis.value}. "
                    f"Stok tersedia {saldo_lama}, diminta {qty}."
                ),
            )
        qty_out = qty
        saldo_baru = saldo_lama - qty

    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Jenis pergerakan tidak dikenal: {jenis}",
        )

    barang.jumlah = saldo_baru
    barang.hpp = hpp_baru
    db_session.add(barang)

    ledger = StockLedger(
        instance_id=instance_id,
        barang_id=barang.id,
        lokasi_id=lokasi_id,
        jenis=jenis,
        harga=_round(harga),
        qty_in=qty_in,
        qty_out=qty_out,
        saldo_qty=saldo_baru,
        hpp=hpp_baru,
        ref_type=ref_type,
        ref_id=ref_id,
    )
    if created_by:
        ledger.created_by = ledger.updated_by = created_by
    db_session.add(ledger)
    return ledger
