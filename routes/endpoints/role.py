from fastapi import APIRouter, Depends
from fastapi_pagination import Params
from sqlmodel import select

from common.enum import OrderEnumSch
from configs.auth import get_current_user
from models.master_user_model import MasterUser
from models.role_model import Role
from schemas.role_sch import RoleByIdSch, RoleCreateSch, RoleSch
from schemas.response_sch import (
    GetResponseBaseSch,
    GetResponsePaginatedSch,
    PostResponseBaseSch,
    create_response,
)
from utils.exceptions.common_exception import IdNotFoundException
import crud

router = APIRouter()


@router.get("", response_model=GetResponsePaginatedSch[RoleSch])
async def get_list(
    search: str | None = None,
    order_by: str | None = "created_at",
    order: OrderEnumSch | None = OrderEnumSch.descendent,
    params: Params = Depends(),
):
    query = select(Role)
    if search:
        query = query.where(Role.name.ilike(f"%{search}%"))
    objs = await crud.role.get_multi_paginated_ordered(
        params=params, order_by=order_by, order=order, query=query
    )
    return create_response(data=objs)


@router.get("/no-page", response_model=GetResponseBaseSch[list[RoleSch]])
async def get_no_page(
    order_by: str | None = "created_at",
    order: OrderEnumSch | None = OrderEnumSch.descendent,
):
    objs = await crud.role.get_all_ordered(order_by=order_by, order=order)
    return create_response(data=objs)


@router.get("/{id}", response_model=GetResponseBaseSch[RoleByIdSch])
async def get_by_id(id: str):
    obj = await crud.role.get(id=id)
    if obj is None:
        raise IdNotFoundException(Role, id)
    return create_response(data=obj)


@router.post("", response_model=PostResponseBaseSch[RoleSch])
async def create(
    sch: RoleCreateSch,
    current_user: MasterUser = Depends(get_current_user),
):
    obj = await crud.role.create(obj_in=sch, created_by=current_user.id)
    return create_response(data=obj)
