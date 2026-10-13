from fastapi import APIRouter, Depends
from fastapi_pagination import Params
from sqlmodel import select

from common.enum import OrderEnumSch
from configs.auth import get_current_user
from models.master_user_model import MasterUser
from schemas.master_user_sch import (
    ChangePasswordSch,
    MasterUserByIdSch,
    MasterUserCreateSch,
    MasterUserSch,
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


@router.get("", response_model=GetResponsePaginatedSch[MasterUserSch])
async def get_list(
    search: str | None = None,
    order_by: str | None = "created_at",
    order: OrderEnumSch | None = OrderEnumSch.descendent,
    params: Params = Depends(),
):
    query = select(MasterUser)
    if search:
        query = query.where(MasterUser.nama.ilike(f"%{search}%"))
    objs = await crud.master_user.get_multi_paginated_ordered(
        params=params, order_by=order_by, order=order, query=query
    )
    return create_response(data=objs)


@router.get("/{id}", response_model=GetResponseBaseSch[MasterUserByIdSch])
async def get_by_id(id: str):
    obj = await crud.master_user.get_full(id=id)
    if obj is None:
        raise IdNotFoundException(MasterUser, id)
    return create_response(data=obj)


@router.post("", response_model=PostResponseBaseSch[MasterUserByIdSch])
async def create(
    sch: MasterUserCreateSch,
    current_user: MasterUser = Depends(get_current_user),
):
    """Buat user baru (dengan mapping instance & role). Password di-hash bcrypt."""
    obj = await crud.master_user.create_user(sch=sch, created_by=current_user.id)
    return create_response(data=obj)


@router.put("/{id}/change-password", response_model=PutResponseBaseSch[MasterUserSch])
async def change_password(
    id: str,
    sch: ChangePasswordSch,
    current_user: MasterUser = Depends(get_current_user),
):
    """Ubah password: verifikasi password lama lalu simpan hash password baru."""
    obj = await crud.master_user.change_password(
        user_id=id, sch=sch, updated_by=current_user.id
    )
    return create_response(data=obj, message="Password berhasil diubah")
