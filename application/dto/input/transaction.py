import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class WithdrawTransactionInput:
    laboratory_id: str
    procedure_id: str

@dataclass
class ListTransactionsInput:
    laboratory_id: Optional[str] = None
    user_id: Optional[str] = None
    transaction_type: Optional[str] = None  # "WITHDRAW" ou "DEPOSIT"
    status: Optional[str] = None  # "AUTHORIZED", "IN_PROGRESS", "COMPLETED", "FAILED"
    start_date: Optional[datetime.datetime] = None
    end_date: Optional[datetime.datetime] = None