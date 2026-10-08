from fastapi import APIRouter, Depends, Header, Request
from fastapi_pagination import Params
from sqlmodel import select

from common.enum import OrderEnumSch
from models.master_vendor_model import MasterVendor
from schemas.master_vendor_sch import (
    MasterVendorByIdSch,
    MasterVendorCreateSch,
    MasterVendorSch,
    MasterVendorUpdateSch,
)
from schemas.response_sch import (
    GetResponseBaseSch,
    GetResponsePaginatedSch,
    PostResponseBaseSch,
    PutResponseBaseSch,
    create_response,
)
from utils.exceptions.common_exception import IdNotFoundException
import crud

router = APIRouter()


def _actor(request: Request) -> str | None:
    if hasattr(request.state, "login_user"):
        return getattr(request.state.login_user, "client_id", None)
    return None


@router.get("", response_model=GetResponsePaginatedSch[MasterVendorSch])
async def get_list(
    order_by: str | None = "created_at",
    order: OrderEnumSch | None = OrderEnumSch.descendent,
    params: Params = Depends(),
    x_instance_id: str = Header(..., alias="X-Instance-Id"),
):
    query = select(MasterVendor).where(MasterVendor.instance_id == x_instance_id)
    objs = await crud.master_vendor.get_multi_paginated_ordered(
        params=params, order_by=order_by, order=order, query=query
    )
    return create_response(data=objs)


@router.get("/{id}", response_model=GetResponseBaseSch[MasterVendorByIdSch])
async def get_by_id(id: str, x_instance_id: str = Header(..., alias="X-Instance-Id")):
    obj = await crud.master_vendor.get(id=id)
    if obj is None or obj.instance_id != x_instance_id:
        raise IdNotFoundException(MasterVendor, id)
    return create_response(data=obj)


@router.post("", response_model=PostResponseBaseSch[MasterVendorSch])
async def create(
    request: Request,
    sch: MasterVendorCreateSch,
    x_instance_id: str = Header(..., alias="X-Instance-Id"),
):
    obj_in = MasterVendor(instance_id=x_instance_id, **sch.model_dump())
    obj = await crud.master_vendor.create(obj_in=obj_in, created_by=_actor(request))
    return create_response(data=obj)


@router.put("/{id}", response_model=PutResponseBaseSch[MasterVendorSch])
async def update(
    id: str,
    request: Request,
    sch: MasterVendorUpdateSch,
    x_instance_id: str = Header(..., alias="X-Instance-Id"),
):
    obj_current = await crud.master_vendor.get(id=id)
    if obj_current is None or obj_current.instance_id != x_instance_id:
        raise IdNotFoundException(MasterVendor, id)
    obj = await crud.master_vendor.update(
        obj_current=obj_current, obj_new=sch, updated_by=_actor(request)
    )
    return create_response(data=obj)
