from fastapi import APIRouter, Depends, Header, Request
from fastapi_pagination import Params
from sqlmodel import select

from common.enum import OrderEnumSch
from models.invoice_model import Invoice
from schemas.invoice_sch import (
    InvoiceByIdSch,
    InvoiceCreateSch,
    InvoiceSch,
    ReturBatchCreateSch,
)
from schemas.response_sch import (
    GetResponseBaseSch,
    GetResponsePaginatedSch,
    PostResponseBaseSch,
    create_response,
)
from utils.exceptions.common_exception import IdNotFoundException
import crud

router = APIRouter()


def _actor(request: Request) -> str | None:
    if hasattr(request.state, "login_user"):
        return getattr(request.state.login_user, "client_id", None)
    return None


@router.get("", response_model=GetResponsePaginatedSch[InvoiceSch])
async def get_list(
    order_by: str | None = "created_at",
    order: OrderEnumSch | None = OrderEnumSch.descendent,
    params: Params = Depends(),
    x_instance_id: str = Header(..., alias="X-Instance-Id"),
):
    query = select(Invoice).where(Invoice.instance_id == x_instance_id)
    objs = await crud.invoice.get_multi_paginated_ordered(
        params=params, order_by=order_by, order=order, query=query
    )
    return create_response(data=objs)


@router.get("/{id}", response_model=GetResponseBaseSch[InvoiceByIdSch])
async def get_by_id(id: str, x_instance_id: str = Header(..., alias="X-Instance-Id")):
    obj = await crud.invoice.get_full(id=id)
    if obj is None or obj.instance_id != x_instance_id:
        raise IdNotFoundException(Invoice, id)
    return create_response(data=obj)


@router.post("", response_model=PostResponseBaseSch[InvoiceByIdSch])
async def create(
    request: Request,
    sch: InvoiceCreateSch,
    x_instance_id: str = Header(..., alias="X-Instance-Id"),
):
    obj = await crud.invoice.create_invoice(
        sch=sch, instance_id=x_instance_id, created_by=_actor(request)
    )
    obj = await crud.invoice.get_full(id=obj.id)
    return create_response(data=obj)


@router.post("/{id}/retur", response_model=PostResponseBaseSch[InvoiceByIdSch])
async def create_retur(
    id: str,
    request: Request,
    sch: ReturBatchCreateSch,
    x_instance_id: str = Header(..., alias="X-Instance-Id"),
):
    await crud.invoice.create_retur(
        invoice_id=id,
        sch=sch,
        instance_id=x_instance_id,
        created_by=_actor(request),
    )
    obj = await crud.invoice.get_full(id=id)
    return create_response(data=obj, message="Retur barang berhasil")
