from fastapi import HTTPException, status
from fastapi_async_sqlalchemy import db
from sqlalchemy.orm import selectinload
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from crud.base_crud import CRUDBase
from models.mapping_user_instance_model import MappingUserInstance
from models.master_instance_model import MasterInstance
from models.master_user_model import MasterUser
from models.role_model import Role
from schemas.master_user_sch import (
    ChangePasswordSch,
    MasterUserCreateSch,
    MasterUserUpdateSch,
)
from utils.security import hash_password, verify_password


class CRUDMasterUser(
    CRUDBase[MasterUser, MasterUserCreateSch, MasterUserUpdateSch]
):
    async def get_by_username(
        self, *, username: str, db_session: AsyncSession | None = None
    ) -> MasterUser | None:
        db_session = db_session or db.session
        result = await db_session.execute(
            select(MasterUser).where(
                func.lower(MasterUser.username) == username.lower()
            )
        )
        return result.scalar_one_or_none()

    async def authenticate(
        self, *, username: str, password: str
    ) -> MasterUser | None:
        """Verifikasi kredensial. Kembalikan user jika cocok & aktif, else None."""
        user = await self.get_by_username(username=username)
        if user is None or not user.is_active:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    async def get_full(self, *, id: str) -> MasterUser | None:
        """Ambil user + mapping instance/role (eager-load untuk response ByIdSch)."""
        result = await db.session.execute(
            select(MasterUser)
            .where(MasterUser.id == id)
            .options(selectinload(MasterUser.instances))
        )
        return result.scalar_one_or_none()

    async def create_user(
        self, *, sch: MasterUserCreateSch, created_by: str | None = None
    ) -> MasterUser:
        db_session: AsyncSession = db.session

        existing = await self.get_by_username(username=sch.username)
        if existing is not None:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                f"Username '{sch.username}' sudah dipakai",
            )

        # Validasi tiap instance_id & role_id sebelum menyimpan apa pun.
        for m in sch.instances:
            if await db_session.get(MasterInstance, m.instance_id) is None:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND,
                    f"Instance {m.instance_id} tidak ditemukan",
                )
            if await db_session.get(Role, m.role_id) is None:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND,
                    f"Role {m.role_id} tidak ditemukan",
                )

        try:
            user = MasterUser(
                nama=sch.nama,
                username=sch.username,
                password=hash_password(sch.password),
                email=sch.email,
                is_active=sch.is_active,
            )
            if created_by:
                user.created_by = user.updated_by = created_by
            db_session.add(user)
            await db_session.flush()

            for m in sch.instances:
                mapping = MappingUserInstance(
                    user_id=user.id,
                    instance_id=m.instance_id,
                    role_id=m.role_id,
                )
                if created_by:
                    mapping.created_by = mapping.updated_by = created_by
                db_session.add(mapping)

            await db_session.commit()
            return await self.get_full(id=user.id)
        except HTTPException:
            await db_session.rollback()
            raise
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

    async def change_password(
        self,
        *,
        user_id: str,
        sch: ChangePasswordSch,
        updated_by: str | None = None,
    ) -> MasterUser:
        db_session: AsyncSession = db.session

        user = await db_session.get(MasterUser, user_id)
        if user is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User tidak ditemukan")

        if not verify_password(sch.old_password, user.password):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "Password lama tidak sesuai"
            )

        try:
            user.password = hash_password(sch.new_password)
            if updated_by:
                user.updated_by = updated_by
            db_session.add(user)
            await db_session.commit()
            await db_session.refresh(user)
            return user
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))


master_user = CRUDMasterUser(MasterUser)
