from crud.base_crud import CRUDBase
from models.master_lokasi_model import MasterLokasi
from schemas.master_lokasi_sch import MasterLokasiCreateSch, MasterLokasiUpdateSch


class CRUDMasterLokasi(
    CRUDBase[MasterLokasi, MasterLokasiCreateSch, MasterLokasiUpdateSch]
):
    pass


master_lokasi = CRUDMasterLokasi(MasterLokasi)
