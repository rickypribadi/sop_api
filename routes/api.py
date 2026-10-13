from fastapi import APIRouter, Depends

from configs.auth import get_current_user
from routes.endpoints import (
    auth,
    worker,
    role,
    master_user,
    master_vendor,
    master_barang,
    master_lokasi,
    purchase,
    invoice,
    payment,
    sales,
    stock_ledger,
    stock_opname,
    laporan,
)

api_router = APIRouter()

# Semua endpoint di bawah ini wajib menyertakan Bearer token (JWT).
_auth = [Depends(get_current_user)]

# Auth (login terbuka, tanpa token)
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Existing
api_router.include_router(
    worker.router, prefix="/worker", tags=["worker"], dependencies=_auth
)
api_router.include_router(
    role.router, prefix="/role", tags=["role"], dependencies=_auth
)

# Master
api_router.include_router(
    master_user.router, prefix="/user", tags=["master-user"], dependencies=_auth
)
api_router.include_router(
    master_vendor.router, prefix="/vendor", tags=["master-vendor"], dependencies=_auth
)
api_router.include_router(
    master_barang.router, prefix="/barang", tags=["master-barang"], dependencies=_auth
)
api_router.include_router(
    master_lokasi.router, prefix="/lokasi", tags=["master-lokasi"], dependencies=_auth
)

# Transaksi
api_router.include_router(
    purchase.router, prefix="/purchase", tags=["purchasing"], dependencies=_auth
)
api_router.include_router(
    invoice.router, prefix="/invoice", tags=["invoice"], dependencies=_auth
)
api_router.include_router(
    payment.router, prefix="/payment", tags=["payment"], dependencies=_auth
)
api_router.include_router(
    sales.router, prefix="/sales", tags=["sales"], dependencies=_auth
)

# Stok & laporan
api_router.include_router(
    stock_ledger.router, prefix="/stock-ledger", tags=["stok"], dependencies=_auth
)
api_router.include_router(
    stock_opname.router, prefix="/stock-opname", tags=["stok"], dependencies=_auth
)
api_router.include_router(
    laporan.router, prefix="/laporan", tags=["laporan"], dependencies=_auth
)
