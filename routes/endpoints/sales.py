from fastapi import APIRouter, Depends, Header, Request
from fastapi_pagination import Params
from sqlmodel import select

from common.enum import OrderEnumSch
from models.sales_model import Sales
from schemas.sales_sch import (
    RefundBatchCreateSch,
    SalesByIdSch,
    SalesCreateSch,
    SalesSch,
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


@router.get("", response_model=GetResponsePaginatedSch[SalesSch])
async def get_list(
    order_by: str | None = "created_at",
    order: OrderEnumSch | None = OrderEnumSch.descendent,
    params: Params = Depends(),
    x_instance_id: str = Header(..., alias="X-Instance-Id"),
):
    query = select(Sales).where(Sales.instance_id == x_instance_id)
    objs = await crud.sales.get_multi_paginated_ordered(
        params=params, order_by=order_by, order=order, query=query
    )
    return create_response(data=objs)


@router.get("/{id}", response_model=GetResponseBaseSch[SalesByIdSch])
async def get_by_id(id: str, x_instance_id: str = Header(..., alias="X-Instance-Id")):
    obj = await crud.sales.get_full(id=id)
    if obj is None or obj.instance_id != x_instance_id:
        raise IdNotFoundException(Sales, id)
    return create_response(data=obj)


@router.post("", response_model=PostResponseBaseSch[SalesByIdSch])
async def create(
    request: Request,
    sch: SalesCreateSch,
    x_instance_id: str = Header(..., alias="X-Instance-Id"),
):
    obj = await crud.sales.create_sales(
        sch=sch, instance_id=x_instance_id, created_by=_actor(request)
    )
    obj = await crud.sales.get_full(id=obj.id)
    return create_response(data=obj)


@router.post("/{id}/refund", response_model=PostResponseBaseSch[SalesByIdSch])
async def create_refund(
    id: str,
    request: Request,
    sch: RefundBatchCreateSch,
    x_instance_id: str = Header(..., alias="X-Instance-Id"),
):
    await crud.sales.create_refund(
        sales_id=id,
        sch=sch,
        instance_id=x_instance_id,
        created_by=_actor(request),
    )
    obj = await crud.sales.get_full(id=id)
    return create_response(data=obj, message="Refund berhasil")
