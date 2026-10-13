from models.worker_model import WorkerBase, WorkerFullBase
from schemas.role_sch import RoleCreateForMappingSch


class WorkerCreateSch(WorkerBase):
    roles: list[RoleCreateForMappingSch] | None
 
class WorkerSch(WorkerFullBase):
    additional_info: str | None = None

class WorkerUpdateSch(WorkerBase):
    pass

class WorkerByIdSch(WorkerSch):
    roles: list[RoleCreateForMappingSch] | None = []
