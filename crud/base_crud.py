from fastapi import HTTPException
from typing import Any, Dict, Generic, List, Type, TypeVar
from common.enum import OrderEnumSch
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_async_sqlalchemy import db
from fastapi_pagination import Params, Page
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlmodel import SQLModel, select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.sql.expression import Select
from sqlalchemy import exc
from datetime import datetime, date, timezone

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
SchemaType = TypeVar("SchemaType", bound=BaseModel)
T = TypeVar("T", bound=SQLModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLModel model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model
        self.db = db

    async def get(
        self, *, id: str | None = None, db_session: AsyncSession | None = None
    ) -> ModelType | None:
        db_session = db_session or db.session
        query = select(self.model).where(self.model.id == id)
        response = await db_session.execute(query)
        return response.scalar_one_or_none()
    
    async def get_by_code_upper(
        self, *, code: str | None = None, db_session: AsyncSession | None = None
    ) -> ModelType | None:
        db_session = db_session or db.session
        query = select(self.model).where(func.upper(self.model.code) == (code or '').upper())
        response = await db_session.execute(query)
        return response.scalar_one_or_none()
    
    async def get_by_name_upper(
        self, *, name: str | None = None, db_session: AsyncSession | None = None
    ) -> ModelType | None:
        db_session = db_session or db.session
        query = select(self.model).where(func.upper(self.model.name) == (name or '').upper())
        response = await db_session.execute(query)
        return response.scalar_one_or_none()

    async def get_by_ids(
        self,
        *,
        list_ids: List[str],
        db_session: AsyncSession | None = None,
    ) -> List[ModelType] | None:
        db_session = db_session or db.session
        response = await db_session.execute(
            select(self.model).where(self.model.id.in_(list_ids))
        )
        return response.scalars().all()

    async def get_count(
        self, db_session: AsyncSession | None = None
    ) -> ModelType | None:
        db_session = db_session or db.session
        response = await db_session.execute(
            select(func.count()).select_from(select(self.model).subquery())
        )
        return response.scalar_one()

    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        query: T | Select[T] | None = None,
        db_session: AsyncSession | None = None,
    ) -> List[ModelType]:
        db_session = db_session or db.session
        if query is None:
            query = select(self.model).offset(
                skip).limit(limit).order_by(self.model.id)
            qurey = "Select * From worker"
        response = await db_session.execute(query)
        return response.mappings().all()

    async def get_multi_paginated(
        self,
        *,
        params: Params | None = Params(),
        query: T | Select[T] | None = None,
        db_session: AsyncSession | None = None,
    ) -> Page[ModelType]:
        db_session = db_session or db.session
        if query is None:
            query = select(self.model)
        return await paginate(db_session, query, params)

    async def get_multi_paginated_ordered(
        self,
        *,
        params: Params | None = Params(),
        order_by: str | None = "updated_at",
        order: OrderEnumSch | None = OrderEnumSch.descendent,
        query: T | Select[T] | None = None,
        db_session: AsyncSession | None = None,
    ) -> Page[ModelType]:
        db_session = db_session or db.session

        columns = self.model.__table__.columns

        if order_by not in columns or order_by is None:
            order_by = self.model.id

        if query is None:
            if order == OrderEnumSch.ascendent:
                query = select(self.model).order_by(columns[order_by].asc())
            else:
                query = select(self.model).order_by(columns[order_by].desc())

        return await paginate(db_session, query, params)

    async def get_multi_ordered(
        self,
        *,
        order_by: str | None = None,
        order: OrderEnumSch | None = OrderEnumSch.ascendent,
        skip: int = 0,
        limit: int = 100,
        db_session: AsyncSession | None = None,
    ) -> List[ModelType]:
        db_session = db_session or db.session

        columns = self.model.__table__.columns

        if order_by not in columns or order_by is None:
            order_by = self.model.id

        if order == OrderEnumSch.ascendent:
            query = (
                select(self.model)
                .offset(skip)
                .limit(limit)
                .order_by(columns[order_by.value].asc())
            )
        else:
            query = (
                select(self.model)
                .offset(skip)
                .limit(limit)
                .order_by(columns[order_by.value].desc())
            )

        response = await db_session.execute(query)
        return response.scalars().all()

    async def create(
        self,
        *,
        obj_in: CreateSchemaType | ModelType,
        created_by: str | None = None,
        db_session: AsyncSession | None = None,
        with_commit: bool | None = True
    ) -> ModelType:
        db_session = db_session or db.session
        db_obj = self.model.model_validate(obj_in)  # type: ignore
        if created_by:
            db_obj.created_by = db_obj.updated_by = created_by

        try:
            db_session.add(db_obj)
            await db_session.flush()
            
            if with_commit:
                await db_session.commit()
                await db_session.refresh(db_obj)
        except exc.IntegrityError as e:
            print(e, flush=True)
            db_session.rollback()
            raise HTTPException(
                status_code=409,
                detail="Resource already exists",
            )
        except Exception as e:
            print(e, flush=True)
            db_session.rollback()
            raise HTTPException(
                status_code=500,
                detail="Gagal membuat data",
            )
        return db_obj

    async def get_all_ordered(
        self,
        *,
        query: T | Select[T] | None = None,
        order_by: str | None = "updated_at",
        order: OrderEnumSch | None = OrderEnumSch.descendent,
        db_session: AsyncSession | None = None,
    ) -> list[ModelType]:
        db_session = db_session or db.session

        columns = self.model.__table__.columns

        if order_by not in columns or order_by is None:
            raise HTTPException(
                status_code=404,
                detail='order_by not in table'
            )

        if query is not None:
            if order == OrderEnumSch.ascendent:
                query = query.order_by(columns[order_by].asc())

            else:
                query = query.order_by(columns[order_by].desc())
        else:
            if order == OrderEnumSch.ascendent:

                query = (
                    select(self.model)
                    .order_by(columns[order_by].asc())
                )
            else:
                query = (
                    select(self.model)
                    .order_by(columns[order_by].desc())
                )

        response = await db_session.execute(query)
        return response.scalars().all()

    async def update(
        self,
        *,
        obj_current: ModelType,
        obj_new: UpdateSchemaType | Dict[str, Any] | ModelType,
        db_session: AsyncSession | None = None,
        updated_by: str | None = None,
        with_commit: bool | None = True
    ) -> ModelType:
        db_session = db_session or db.session
        obj_data = jsonable_encoder(obj_current)

        if isinstance(obj_new, dict):
            update_data = obj_new
        else:
            update_data = obj_new.dict(
                exclude_unset=True
            )  # This tells Pydantic to not include the values that were not sent
        for field in obj_data:
            if field in update_data:
                column_type = type(getattr(obj_current, field, None))
                if column_type == date and type(update_data[field]) == str:
                    setattr(obj_current, field, datetime.fromisoformat(update_data[field]).date())
                elif column_type == datetime and type(update_data[field]) == str:
                    setattr(obj_current, field, datetime.fromisoformat(update_data[field]))
                else:
                    setattr(obj_current, field, update_data[field])
            elif updated_by and updated_by != '' and field == "updated_by":
                setattr(obj_current, field, updated_by)
            elif field == "updated_at":
                setattr(obj_current, field, datetime.now(timezone.utc).replace(tzinfo=None))

        db_session.add(obj_current)
        if with_commit:
            await db_session.commit()
            await db_session.refresh(obj_current)
            
        return obj_current

    async def remove(
        self, *, id: str, db_session: AsyncSession | None = None
    ) -> ModelType:
        db_session = db_session or db.session
        response = await db_session.execute(
            select(self.model).where(self.model.id == id)
        )
        obj = response.scalar_one()
        await db_session.delete(obj)
        await db_session.commit()
        return obj

    async def get_list(
        self,
        *,
        query: T | Select[T] | None = None,
        order_by: str | None = None,
        order: OrderEnumSch | None = OrderEnumSch.ascendent,
        db_session: AsyncSession | None = None,
    ) -> list[ModelType]:
        db_session = db_session or db.session

        columns = self.model.__table__.columns

        if order_by not in columns or order_by is None:
            raise HTTPException(
                status_code=404,
                detail='order_by not in table'
            )

        if query is not None:
            if order == OrderEnumSch.ascendent:
                query = query.order_by(columns[order_by].asc())

            else:
                query = query.order_by(columns[order_by].desc())
        else:
            if order == OrderEnumSch.ascendent:

                query = (
                    select(self.model)
                    .order_by(columns[order_by].asc())
                )
            else:
                query = (
                    select(self.model)
                    .order_by(columns[order_by].desc())
                )

        response = await db_session.execute(query)
        return response.all()