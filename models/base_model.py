from datetime import datetime

from sqlalchemy.orm import declared_attr
from sqlmodel import SQLModel as _SQLModel, Field
from stringcase import snakecase
from ulid import ULID


class SQLModel(_SQLModel):
    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:
        return snakecase(cls.__name__)


def generate_ulid() -> str:
    return str(ULID())


class BaseFieldULIDModel(SQLModel):
    id: str | None = Field(
        default_factory=generate_ulid,
        primary_key=True,
        index=True,
        nullable=False,
        max_length=26,
        unique=True,
    )


class BaseULIDModel(BaseFieldULIDModel):
    """RawModel: id + audit fields (created/updated)."""

    created_by: str = Field(nullable=False, default="admin")
    updated_by: str = Field(nullable=False, default="admin")
    created_at: datetime | None = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = Field(default_factory=datetime.utcnow)


# Alias agar konsisten dengan penamaan di sheet Excel (RawModel).
RawModel = BaseULIDModel


class BaseInstanceModel(BaseULIDModel):
    """BaseModel: RawModel + instance scope (multi-tenant per instance)."""

    instance_id: str = Field(nullable=False, foreign_key="master_instance.id")


class VoidFieldModel(SQLModel):
    """Field pembatalan transaksi (void)."""

    is_void: bool = Field(default=False, nullable=False)
    void_by: str | None = Field(default=None, nullable=True)
    void_at: datetime | None = Field(default=None, nullable=True)
    void_reason: str | None = Field(default=None, nullable=True)
