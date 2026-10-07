from sqlmodel import SQLModel

class AccessToken(SQLModel):
    active: bool
    scope: str | None= None
    exp: int | None= None
    client_id: str | None= None
    authorities: list[str] | None= None
    projects: list[str] | None = []
    companies: list[str] | None = []
    segments: list[str] | None = []
    token: str | None = None
    name: str | None = None
    worker_id: str | None = None
    worker_name: str | None = None
    department_ids: list[str] | None = []
    department_names: list[str] | None = []
    department_codes: list[str] | None = []
    is_full_arsip: bool | None = False
    is_arsip_ajb: bool | None = False
    is_arsip_holding: bool | None = False
    is_manajemen: bool | None = False