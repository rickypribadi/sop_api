from crud.base_crud import CRUDBase
from models.master_barang_model import MasterBarang
from schemas.master_barang_sch import MasterBarangCreateSch, MasterBarangUpdateSch


class CRUDMasterBarang(
    CRUDBase[MasterBarang, MasterBarangCreateSch, MasterBarangUpdateSch]
):
    pass


master_barang = CRUDMasterBarang(MasterBarang)
