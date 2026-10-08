from crud.base_crud import CRUDBase
from models.master_vendor_model import MasterVendor
from schemas.master_vendor_sch import MasterVendorCreateSch, MasterVendorUpdateSch


class CRUDMasterVendor(
    CRUDBase[MasterVendor, MasterVendorCreateSch, MasterVendorUpdateSch]
):
    pass


master_vendor = CRUDMasterVendor(MasterVendor)
