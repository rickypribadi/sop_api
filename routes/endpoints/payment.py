from fastapi import APIRouter, Depends, Header
from fastapi_pagination import Params
from sqlmodel import select

from common.enum import OrderEnumSch
from configs.auth import get_current_user
from models.master_user_model import MasterUser
from models.payment_model import Payment
from schemas.payment_sch import PaymentByIdSch, PaymentCreateSch, PaymentSch
from schemas.response_sch import (
    GetResponseBaseSch,
    GetResponsePaginatedSch,
    PostResponseBaseSch,
    create_response,
)
from utils.exceptions.common_exception import IdNotFoundException
import crud

router = APIRouter()


@router.get("", response_model=GetResponsePaginatedSch[PaymentSch])
async def get_list(
    order_by: str | None = "created_at",
    order: OrderEnumSch | None = OrderEnumSch.descendent,
    params: Params = Depends(),
    x_instance_id: str = Header(..., alias="X-Instance-Id"),
):
    query = select(Payment).where(Payment.instance_id == x_instance_id)
    objs = await crud.payment.get_multi_paginated_ordered(
        params=params, order_by=order_by, order=order, query=query
    )
    return create_response(data=objs)


@router.get("/{id}", response_model=GetResponseBaseSch[PaymentByIdSch])
async def get_by_id(id: str, x_instance_id: str = Header(..., alias="X-Instance-Id")):
    obj = await crud.payment.get(id=id)
    if obj is None or obj.instance_id != x_instance_id:
        raise IdNotFoundException(Payment, id)
    return create_response(data=obj)


@router.post("", response_model=PostResponseBaseSch[PaymentSch])
async def create(
    sch: PaymentCreateSch,
    x_instance_id: str = Header(..., alias="X-Instance-Id"),
    current_user: MasterUser = Depends(get_current_user),
):
    obj = await crud.payment.create_payment(
        sch=sch, instance_id=x_instance_id, created_by=current_user.id
    )
    return create_response(data=obj)
