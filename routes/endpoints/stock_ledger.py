from fastapi import APIRouter, Depends, Header, Query
from fastapi_pagination import Params
from sqlmodel import select

from common.enum import OrderEnumSch
from models.stock_ledger_model import StockLedger
from schemas.response_sch import GetResponsePaginatedSch, create_response
from schemas.stock_ledger_sch import StockLedgerSch
import crud

router = APIRouter()


@router.get("", response_model=GetResponsePaginatedSch[StockLedgerSch])
async def get_list(
    barang_id: str | None = Query(default=None),
    lokasi_id: str | None = Query(default=None),
    order_by: str | None = "tanggal",
    order: OrderEnumSch | None = OrderEnumSch.ascendent,
    params: Params = Depends(),
    x_instance_id: str = Header(..., alias="X-Instance-Id"),
):
    """Kartu stok (ledger) dengan jejak HPP moving average per barang/lokasi."""
    query = select(StockLedger).where(StockLedger.instance_id == x_instance_id)
    if barang_id:
        query = query.where(StockLedger.barang_id == barang_id)
    if lokasi_id:
        query = query.where(StockLedger.lokasi_id == lokasi_id)
    objs = await crud.stock_ledger.get_multi_paginated_ordered(
        params=params, order_by=order_by, order=order, query=query
    )
    return create_response(data=objs)
