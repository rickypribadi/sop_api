from fastapi import APIRouter, Depends, Header, Request
from fastapi_pagination import Params
from sqlmodel import select

from common.enum import OrderEnumSch
from models.purchase_model import Purchase
from schemas.purchase_sch import (
    PlacementBatchCreateSch,
    PlacementSch,
    PurchaseByIdSch,
    PurchaseCreateSch,
    PurchaseSch,
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


@router.get("", response_model=GetResponsePaginatedSch[PurchaseSch])
async def get_list(
    order_by: str | None = "created_at",
    order: OrderEnumSch | None = OrderEnumSch.descendent,
    params: Params = Depends(),
    x_instance_id: str = Header(..., alias="X-Instance-Id"),
):
    query = select(Purchase).where(Purchase.instance_id == x_instance_id)
    objs = await crud.purchase.get_multi_paginated_ordered(
        params=params, order_by=order_by, order=order, query=query
    )
    return create_response(data=objs)


@router.get("/{id}", response_model=GetResponseBaseSch[PurchaseByIdSch])
async def get_by_id(id: str, x_instance_id: str = Header(..., alias="X-Instance-Id")):
    obj = await crud.purchase.get_full(id=id)
    if obj is None or obj.instance_id != x_instance_id:
        raise IdNotFoundException(Purchase, id)
    return create_response(data=obj)


@router.post("", response_model=PostResponseBaseSch[PurchaseByIdSch])
async def create(
    request: Request,
    sch: PurchaseCreateSch,
    x_instance_id: str = Header(..., alias="X-Instance-Id"),
):
    obj = await crud.purchase.create_purchase(
        sch=sch, instance_id=x_instance_id, created_by=_actor(request)
    )
    obj = await crud.purchase.get_full(id=obj.id)
    return create_response(data=obj)


@router.post(
    "/{id}/placements", response_model=PostResponseBaseSch[list[PlacementSch]]
)
async def create_placement(
    id: str,
    request: Request,
    sch: PlacementBatchCreateSch,
    x_instance_id: str = Header(..., alias="X-Instance-Id"),
):
    objs = await crud.purchase.create_placement(
        purchase_id=id,
        sch=sch,
        instance_id=x_instance_id,
        created_by=_actor(request),
    )
    return create_response(data=objs, message="Penempatan barang berhasil")
