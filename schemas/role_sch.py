from models.role_model import RoleBase, RoleFullBase
from sqlmodel import SQLModel

class RoleCreateSch(RoleBase):
    pass

class RoleSch(RoleFullBase):
    pass

class RoleUpdateSch(RoleBase):
    pass

class RoleByIdSch(RoleFullBase):
    pass

class RoleCreateForMappingSch(SQLModel):
    id: str | None
    name: str | None
