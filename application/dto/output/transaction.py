from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass(frozen=True)
class TransactionItemOutput:
    material_id: str
    quantity: int


@dataclass(frozen=True)
class WithdrawTransactionOutput:
    transaction_id: str
    transaction_type: str
    status: str
    laboratory_id: str
    procedure_id: str
    created_at: datetime
    authorized_at: datetime
    items: List[TransactionItemOutput]

import datetime
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ListTransactionsInput:
    laboratory_id: Optional[str] = None
    user_id: Optional[str] = None
    transaction_type: Optional[str] = None  # "WITHDRAW" ou "DEPOSIT"
    status: Optional[str] = None  # "AUTHORIZED", "IN_PROGRESS", "COMPLETED", "FAILED"
    start_date: Optional[datetime.datetime] = None
    end_date: Optional[datetime.datetime] = None


@dataclass
class MaterialItemOutput:
    id: str
    name: str
    quantity: int


@dataclass
class ProcedureOutput:
    id: str
    name: str
    items: List[MaterialItemOutput]


@dataclass
class TransactionListItemOutput:
    employee_id: str
    procedure: Optional[ProcedureOutput]
    timestamp: datetime.datetime


@dataclass
class ListTransactionsOutput:
    transactions: List[TransactionListItemOutput]