from abc import abstractmethod, ABC
from typing import Optional

from domain.entities.transaction import Transaction
from domain.value_objects.ids import TransactionId


class TransactionRepository(ABC):

    @abstractmethod
    async def save(self, transaction: Transaction) -> None:
        pass

    @abstractmethod
    async def find_by_id(self, transaction_id: TransactionId) -> Optional[Transaction]:
        pass

    @abstractmethod
    async def exists(self, transaction_id: TransactionId) -> bool:
        pass