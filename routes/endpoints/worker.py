from fastapi import APIRouter, status, HTTPException, Request, Depends
from sqlmodel import select, or_, String, cast
from sqlalchemy.orm import selectinload
from fastapi_pagination import Params
from schemas.worker_sch import (WorkerSch, WorkerUpdateSch, WorkerCreateSch, WorkerByIdSch)
from schemas.response_sch import (PostResponseBaseSch, GetResponseBaseSch, GetResponsePaginatedSch, create_response)
from common.enum import OrderEnumSch
from models.worker_model import Worker
import crud
from utils.exceptions.common_exception import IdNotFoundException

router = APIRouter()

@router.get("", response_model=GetResponsePaginatedSch[WorkerSch])
async def get_list(
    search:str | None = None, 
    order_by:str | None = "created_at",
    order: OrderEnumSch | None = OrderEnumSch.descendent,
    params: Params=Depends()
):
    objs = await crud.worker.get_paginated(params=params, search=search, order_by=order_by, order=order)
    return create_response(data=objs)

@router.get("/no-page", response_model=GetResponseBaseSch[list[WorkerSch]])
async def get_no_page(
    search:str | None = None,
    order_by:str | None = "created_at",
    order: OrderEnumSch | None = OrderEnumSch.descendent
):
    objs = await crud.worker.get_no_paginated(search=search, order_by=order_by, order=order)
    return create_response(data=objs)

@router.get("/{id}", response_model=GetResponseBaseSch[WorkerByIdSch])
async def get_by_id(id: str):

    obj = await crud.worker.get_by_id(id=id)
    if obj is None:
        raise IdNotFoundException(Worker, id)
    return create_response(data=obj)

@router.get("/by-email/{email}", response_model=GetResponseBaseSch[WorkerByIdSch])
async def get_by_client_id(email: str):

    obj = await crud.worker.get_by_client_id(email=email)
    if obj is None:
        raise IdNotFoundException(Worker, id)
    return create_response(data=obj)


@router.post("", response_model=PostResponseBaseSch[WorkerSch], status_code=status.HTTP_201_CREATED)
async def create(request: Request, sch: WorkerCreateSch):
    
    """Create a new object"""
    if hasattr(request.state, 'login_user'):
        login_user=request.state.login_user
    obj = await crud.worker.create(sch=sch, created_by=login_user.client_id)
    worker = await crud.worker.get_by_id(id=obj.id)
    return create_response(data=worker)

@router.put("/{id}", response_model=PostResponseBaseSch[WorkerByIdSch], status_code=status.HTTP_201_CREATED)
async def update(id: str, request: Request, obj_new: WorkerUpdateSch):
    
    if hasattr(request.state, 'login_user'):
        login_user = request.state.login_user
    obj_current = await crud.worker.get(id=id)
    if not obj_current:
        raise HTTPException(status_code=404, detail=f"Worker tidak ditemukan")
    obj_updated = await crud.worker.update(obj_current=obj_current, obj_new=obj_new, updated_by=login_user.client_id)
    response_obj = await crud.worker.get_by_id(id=id)
    return create_response(data=response_obj)





