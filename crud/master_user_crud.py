from fastapi import HTTPException, status
from fastapi_async_sqlalchemy import db
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from crud.base_crud import CRUDBase
from models.master_user_model import MasterUser
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

        try:
            user = MasterUser(
                nama=sch.nama,
                username=sch.username,
                password=hash_password(sch.password),
                is_active=sch.is_active,
            )
            if created_by:
                user.created_by = user.updated_by = created_by
            db_session.add(user)
            await db_session.commit()
            await db_session.refresh(user)
            return user
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
