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
