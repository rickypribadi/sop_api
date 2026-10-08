from fastapi import APIRouter, Depends, Header
from fastapi_pagination import Params
from sqlmodel import select

from common.enum import OrderEnumSch
from configs.auth import get_current_user
from models.master_user_model import MasterUser
from models.stock_opname_model import StockOpname
from schemas.response_sch import (
    GetResponseBaseSch,
    GetResponsePaginatedSch,
    PostResponseBaseSch,
    create_response,
)
from schemas.stock_opname_sch import (
    StockOpnameByIdSch,
    StockOpnameCreateSch,
    StockOpnameSch,
)
from utils.exceptions.common_exception import IdNotFoundException
import crud

router = APIRouter()


@router.get("", response_model=GetResponsePaginatedSch[StockOpnameSch])
async def get_list(
    order_by: str | None = "created_at",
    order: OrderEnumSch | None = OrderEnumSch.descendent,
    params: Params = Depends(),
    x_instance_id: str = Header(..., alias="X-Instance-Id"),
):
    query = select(StockOpname).where(StockOpname.instance_id == x_instance_id)
    objs = await crud.stock_opname.get_multi_paginated_ordered(
        params=params, order_by=order_by, order=order, query=query
    )
    return create_response(data=objs)


@router.get("/{id}", response_model=GetResponseBaseSch[StockOpnameByIdSch])
async def get_by_id(id: str, x_instance_id: str = Header(..., alias="X-Instance-Id")):
    obj = await crud.stock_opname.get_full(id=id)
    if obj is None or obj.instance_id != x_instance_id:
        raise IdNotFoundException(StockOpname, id)
    return create_response(data=obj)


@router.post("", response_model=PostResponseBaseSch[StockOpnameByIdSch])
async def create(
    sch: StockOpnameCreateSch,
    x_instance_id: str = Header(..., alias="X-Instance-Id"),
    current_user: MasterUser = Depends(get_current_user),
):
    obj = await crud.stock_opname.create_opname(
        sch=sch, instance_id=x_instance_id, created_by=current_user.id
    )
    obj = await crud.stock_opname.get_full(id=obj.id)
    return create_response(data=obj)
