from datetime import datetime

from sqlmodel import SQLModel


class MasterUserCreateSch(SQLModel):
    nama: str
    username: str
    password: str
    is_active: bool = True


class MasterUserUpdateSch(SQLModel):
    nama: str | None = None
    is_active: bool | None = None


class ChangePasswordSch(SQLModel):
    old_password: str
    new_password: str


# Response schema TANPA password (hash tidak pernah dikembalikan).
class MasterUserSch(SQLModel):
    id: str
    nama: str
    username: str
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
    created_by: str | None = None
    updated_by: str | None = None


class MasterUserByIdSch(MasterUserSch):
    pass
