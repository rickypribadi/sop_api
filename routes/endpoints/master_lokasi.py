from fastapi import APIRouter, Depends, Header
from fastapi_pagination import Params
from sqlmodel import select

from common.enum import OrderEnumSch
from configs.auth import get_current_user
from models.master_lokasi_model import MasterLokasi
from models.master_user_model import MasterUser
from schemas.master_lokasi_sch import (
    MasterLokasiByIdSch,
    MasterLokasiCreateSch,
    MasterLokasiSch,
    MasterLokasiUpdateSch,
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


@router.get("", response_model=GetResponsePaginatedSch[MasterLokasiSch])
async def get_list(
    order_by: str | None = "created_at",
    order: OrderEnumSch | None = OrderEnumSch.descendent,
    params: Params = Depends(),
    x_instance_id: str = Header(..., alias="X-Instance-Id"),
):
    query = select(MasterLokasi).where(MasterLokasi.instance_id == x_instance_id)
    objs = await crud.master_lokasi.get_multi_paginated_ordered(
        params=params, order_by=order_by, order=order, query=query
    )
    return create_response(data=objs)


@router.get("/{id}", response_model=GetResponseBaseSch[MasterLokasiByIdSch])
async def get_by_id(id: str, x_instance_id: str = Header(..., alias="X-Instance-Id")):
    obj = await crud.master_lokasi.get(id=id)
    if obj is None or obj.instance_id != x_instance_id:
        raise IdNotFoundException(MasterLokasi, id)
    return create_response(data=obj)


@router.post("", response_model=PostResponseBaseSch[MasterLokasiSch])
async def create(
    sch: MasterLokasiCreateSch,
    x_instance_id: str = Header(..., alias="X-Instance-Id"),
    current_user: MasterUser = Depends(get_current_user),
):
    obj_in = MasterLokasi(instance_id=x_instance_id, **sch.model_dump())
    obj = await crud.master_lokasi.create(obj_in=obj_in, created_by=current_user.id)
    return create_response(data=obj)


@router.put("/{id}", response_model=PutResponseBaseSch[MasterLokasiSch])
async def update(
    id: str,
    sch: MasterLokasiUpdateSch,
    x_instance_id: str = Header(..., alias="X-Instance-Id"),
    current_user: MasterUser = Depends(get_current_user),
):
    obj_current = await crud.master_lokasi.get(id=id)
    if obj_current is None or obj_current.instance_id != x_instance_id:
        raise IdNotFoundException(MasterLokasi, id)
    obj = await crud.master_lokasi.update(
        obj_current=obj_current, obj_new=sch, updated_by=current_user.id
    )
    return create_response(data=obj)
