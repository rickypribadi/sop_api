from fastapi import HTTPException
from fastapi_async_sqlalchemy import db
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlmodel import and_, select, or_
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from crud.base_crud import CRUDBase
from models import Worker, WorkerRole, Department
from schemas.worker_sch import WorkerCreateSch, WorkerUpdateSch, WorkerSch
from common.enum import OrderEnumSch
from itertools import product
import crud

class CRUDWorker(CRUDBase[Worker, WorkerCreateSch, WorkerUpdateSch]):
    
    async def get_paginated(self, *, params: Params, **kwargs):
        query = self.base_query()
        query = self.join_department(query=query)
        query = self.create_filter(query=query, filter=kwargs)

        return await paginate(db.session, query, params)
    
    async def get_no_paginated(self, **kwargs):
        query = self.base_query()
        query = self.create_filter(query=query, filter=kwargs)

        response = await db.session.execute(query)
        return response.mappings().all()
    
    async def get_by_id(self, *, id:str) -> Worker:
        worker = await self.fetch_worker(id=id)
        if not worker:
            return None
        
        worker = WorkerSch(**worker._mapping)
        return worker
       
    async def get_by_client_id(self, *, email:str):
        worker = await self.fetch_worker_by_email(email=email)
        if not worker:
            return None
        
        worker = WorkerSch(**worker._mapping)
        return worker
    
    async def create(self, *, sch:WorkerCreateSch, created_by:str, db_session: AsyncSession | None = None) -> Worker:
        db_session = db_session or db.session

        worker = Worker.model_validate(sch.model_dump())
        db_session.add(worker)

        await db_session.flush()

        for role in sch.roles:
            mapping = WorkerRole(worker_id=worker.id, role_id=role.id)
            db_session.add(mapping)

        if created_by:
            worker.created_by = worker.updated_by = created_by

        await db_session.commit()

        return worker
    
    async def fetch_worker(self, *, id: str):
        query = self.base_query()
        query = query.where(Worker.id == id)
        response = await db.session.execute(query)
        return response.one_or_none()
    
    async def fetch_worker_by_email(self, *, email: str):
        query = self.base_query()
        query = query.where(Worker.email == email)
        response = await db.session.execute(query)
        return response.one_or_none()

    def base_query(self):
        return select(
            *Worker.__table__.columns)
    
    def create_filter(self, *, query, filter:dict):
        if filter.get("search"):
            search = filter.get("search")
            query = query.filter(
                or_(
                    Worker.email.ilike(f'%{search}%'),
                    Worker.name.ilike(f'%{search}%'),
                )
            )
        
        if filter.get("order_by"):
          if filter.get("order"):
             order_column = getattr(Worker, filter.get('order_by'))
             if order_column is None:
                raise HTTPException(status_code=400, detail=f'Field {filter.get("order_by")} not found')
             order = filter.get("order")
             if order == OrderEnumSch.descendent:
                   query = query.order_by(order_column.desc())
             if order == OrderEnumSch.ascendent:
                   query = query.order_by(order_column.asc())

        return query
    
    def join_department(self, *, query):
        query = query.outerjoin(Department, Department.id == Worker.department_id)
        return query
worker = CRUDWorker(Worker)
