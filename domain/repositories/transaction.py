import datetime
from abc import abstractmethod, ABC
from typing import Optional, List

from domain.entities.transaction import Transaction
from domain.value_objects.enums import TransactionStatus, TransactionType
from domain.value_objects.ids import TransactionId, LaboratoryId, UserId


class TransactionRepository(ABC):

    @abstractmethod
    async def save(self, transaction: Transaction) -> None:
        pass

    @abstractmethod
    async def find_by_id(self, transaction_id: TransactionId) -> Optional[Transaction]:
        pass

    @abstractmethod
    async def find_with_filters(
            self,
            laboratory_id: Optional[LaboratoryId] = None,
            user_id: Optional[UserId] = None,
            transaction_type: Optional[TransactionType] = None,
            status: Optional[TransactionStatus] = None,
            start_date: Optional[datetime.datetime] = None,
            end_date: Optional[datetime.datetime] = None
    ) -> List[Transaction]:
        pass