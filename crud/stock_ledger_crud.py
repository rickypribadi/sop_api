from crud.base_crud import CRUDBase
from models.stock_ledger_model import StockLedger
from schemas.stock_ledger_sch import StockLedgerSch


class CRUDStockLedger(CRUDBase[StockLedger, StockLedgerSch, StockLedgerSch]):
    pass


stock_ledger = CRUDStockLedger(StockLedger)
