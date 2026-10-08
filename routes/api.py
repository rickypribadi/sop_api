from fastapi import APIRouter

from routes.endpoints import (
    worker,
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

# Existing
api_router.include_router(worker.router, prefix="/worker", tags=["worker"])

# Master
api_router.include_router(master_user.router, prefix="/user", tags=["master-user"])
api_router.include_router(
    master_vendor.router, prefix="/vendor", tags=["master-vendor"]
)
api_router.include_router(
    master_barang.router, prefix="/barang", tags=["master-barang"]
)
api_router.include_router(
    master_lokasi.router, prefix="/lokasi", tags=["master-lokasi"]
)

# Transaksi
api_router.include_router(purchase.router, prefix="/purchase", tags=["purchasing"])
api_router.include_router(invoice.router, prefix="/invoice", tags=["invoice"])
api_router.include_router(payment.router, prefix="/payment", tags=["payment"])
api_router.include_router(sales.router, prefix="/sales", tags=["sales"])

# Stok & laporan
api_router.include_router(
    stock_ledger.router, prefix="/stock-ledger", tags=["stok"]
)
api_router.include_router(
    stock_opname.router, prefix="/stock-opname", tags=["stok"]
)
api_router.include_router(laporan.router, prefix="/laporan", tags=["laporan"])
