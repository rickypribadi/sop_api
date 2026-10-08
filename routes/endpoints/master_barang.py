from fastapi import APIRouter, Depends, Header
from fastapi_pagination import Params
from sqlmodel import select

from common.enum import OrderEnumSch
from configs.auth import get_current_user
from models.master_barang_model import MasterBarang
from models.master_user_model import MasterUser
from schemas.master_barang_sch import (
    MasterBarangByIdSch,
    MasterBarangCreateSch,
    MasterBarangSch,
    MasterBarangUpdateSch,
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


@router.get("", response_model=GetResponsePaginatedSch[MasterBarangSch])
async def get_list(
    search: str | None = None,
    order_by: str | None = "created_at",
    order: OrderEnumSch | None = OrderEnumSch.descendent,
    params: Params = Depends(),
    x_instance_id: str = Header(..., alias="X-Instance-Id"),
):
    query = select(MasterBarang).where(MasterBarang.instance_id == x_instance_id)
    if search:
        query = query.where(MasterBarang.nama.ilike(f"%{search}%"))
    objs = await crud.master_barang.get_multi_paginated_ordered(
        params=params, order_by=order_by, order=order, query=query
    )
    return create_response(data=objs)


@router.get("/{id}", response_model=GetResponseBaseSch[MasterBarangByIdSch])
async def get_by_id(id: str, x_instance_id: str = Header(..., alias="X-Instance-Id")):
    obj = await crud.master_barang.get(id=id)
    if obj is None or obj.instance_id != x_instance_id:
        raise IdNotFoundException(MasterBarang, id)
    return create_response(data=obj)


@router.post("", response_model=PostResponseBaseSch[MasterBarangSch])
async def create(
    sch: MasterBarangCreateSch,
    x_instance_id: str = Header(..., alias="X-Instance-Id"),
    current_user: MasterUser = Depends(get_current_user),
):
    obj_in = MasterBarang(instance_id=x_instance_id, **sch.model_dump())
    obj = await crud.master_barang.create(obj_in=obj_in, created_by=current_user.id)
    return create_response(data=obj)


@router.put("/{id}", response_model=PutResponseBaseSch[MasterBarangSch])
async def update(
    id: str,
    sch: MasterBarangUpdateSch,
    x_instance_id: str = Header(..., alias="X-Instance-Id"),
    current_user: MasterUser = Depends(get_current_user),
):
    obj_current = await crud.master_barang.get(id=id)
    if obj_current is None or obj_current.instance_id != x_instance_id:
        raise IdNotFoundException(MasterBarang, id)
    obj = await crud.master_barang.update(
        obj_current=obj_current, obj_new=sch, updated_by=current_user.id
    )
    return create_response(data=obj)
