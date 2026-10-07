# Reference scaffold models
from .department_model import Department
from .role_model import Role
from .worker_model import Worker
from .worker_role_model import WorkerRole

# Master
from .master_instance_model import MasterInstance
from .master_user_model import MasterUser
from .mapping_user_instance_model import MappingUserInstance
from .master_vendor_model import MasterVendor
from .master_barang_model import MasterBarang
from .master_lokasi_model import MasterLokasi

# Purchasing
from .purchase_model import Purchase
from .purchase_detail_model import PurchaseDetail
from .purchase_detail_placement_model import PurchaseDetailPlacement

# Invoice & payment
from .invoice_model import Invoice
from .invoice_detail_model import InvoiceDetail
from .payment_model import Payment

# Sales
from .sales_model import Sales
from .sales_detail_model import SalesDetail

# Stock
from .stock_ledger_model import StockLedger
from .stock_opname_model import StockOpname
from .stock_opname_detail_model import StockOpnameDetail

__all__ = [
    "Department",
    "Role",
    "Worker",
    "WorkerRole",
    "MasterInstance",
    "MasterUser",
    "MappingUserInstance",
    "MasterVendor",
    "MasterBarang",
    "MasterLokasi",
    "Purchase",
    "PurchaseDetail",
    "PurchaseDetailPlacement",
    "Invoice",
    "InvoiceDetail",
    "Payment",
    "Sales",
    "SalesDetail",
    "StockLedger",
    "StockOpname",
    "StockOpnameDetail",
]
