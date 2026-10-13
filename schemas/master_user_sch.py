from datetime import datetime

from pydantic import field_validator
from sqlmodel import SQLModel


class UserInstanceRoleCreateSch(SQLModel):
    instance_id: str
    role_id: str


class MasterUserCreateSch(SQLModel):
    nama: str
    username: str
    password: str
    email: str | None = None
    is_active: bool = True
    # Minimal satu mapping instance + role per user.
    instances: list[UserInstanceRoleCreateSch]

    @field_validator("instances")
    def _min_one_instance(cls, v):
        if not v:
            raise ValueError("User harus memiliki minimal satu instance & role")
        return v


class MasterUserUpdateSch(SQLModel):
    nama: str | None = None
    email: str | None = None
    is_active: bool | None = None


class ChangePasswordSch(SQLModel):
    old_password: str
    new_password: str


# ---- Response (tanpa password) ----
class UserInstanceRoleSch(SQLModel):
    id: str
    instance_id: str
    role_id: str
    is_active: bool


class MasterUserSch(SQLModel):
    id: str
    nama: str
    username: str
    email: str | None = None
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
    created_by: str | None = None
    updated_by: str | None = None


class MasterUserByIdSch(MasterUserSch):
    instances: list[UserInstanceRoleSch] = []
