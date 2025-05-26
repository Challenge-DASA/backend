import datetime
from dataclasses import dataclass

from typing import Optional, List

from domain.entities.material import MaterialId
from domain.entities.transaction_item import TransactionItem
from domain.exceptions import InvalidTransactionStateError
from domain.value_objects.enums import TransactionType, TransactionStatus
from domain.value_objects.ids import TransactionId, LaboratoryId, UserId, ProcedureId


@dataclass
class Transaction:
    transaction_id: TransactionId
    transaction_type: TransactionType
    status: TransactionStatus
    laboratory_id: LaboratoryId
    user_id: UserId
    procedure_id: Optional[ProcedureId]
    created_at: datetime.datetime
    authorized_at: Optional[datetime.datetime]
    completed_at: Optional[datetime.datetime]
    items: List[TransactionItem]

    def start_processing(self) -> None:
        if self.status != TransactionStatus.AUTHORIZED:
            raise InvalidTransactionStateError(f"Cannot start processing transaction in status {self.status}")
        self.status = TransactionStatus.IN_PROGRESS

    def complete(self) -> None:
        if self.status != TransactionStatus.IN_PROGRESS:
            raise InvalidTransactionStateError(f"Cannot complete transaction in status {self.status}")
        self.status = TransactionStatus.COMPLETED
        self.completed_at = datetime.datetime.now(datetime.UTC)

    def fail(self) -> None:
        if self.status == TransactionStatus.COMPLETED:
            raise InvalidTransactionStateError(f"Cannot fail completed transaction")
        self.status = TransactionStatus.FAILED

    def is_authorized(self) -> bool:
        return self.status == TransactionStatus.AUTHORIZED

    def is_completed(self) -> bool:
        return self.status == TransactionStatus.COMPLETED

    def get_material_quantities(self) -> List[tuple[MaterialId, int]]:
        return [(item.material_id, item.quantity) for item in self.items]