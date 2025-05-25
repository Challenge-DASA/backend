from abc import ABC, abstractmethod
from typing import Optional, List

from domain.entities.material import Material
from domain.entities.material_balance import MaterialBalance
from domain.value_objects.ids import MaterialId, LaboratoryId

class MaterialRepository(ABC):
    @abstractmethod
    async def find_by_id(self, material_id: MaterialId) -> Optional[Material]:
        pass

    @abstractmethod
    async def find_by_multiple_ids(self, material_ids: List[MaterialId]) -> List[Material]:
        pass

    @abstractmethod
    async def exists(self, material_id: MaterialId) -> bool:
        pass


class MaterialBalanceRepository(ABC):
    @abstractmethod
    async def save(self, balance: MaterialBalance) -> None:
        pass

    @abstractmethod
    async def find_by_material_and_laboratory(
            self,
            material_id: MaterialId,
            laboratory_id: LaboratoryId
    ) -> Optional[MaterialBalance]:
        pass

    @abstractmethod
    async def find_by_laboratory(self, laboratory_id: LaboratoryId) -> List[MaterialBalance]:
        pass

    @abstractmethod
    async def find_multiple_by_laboratory(
            self,
            material_ids: List[MaterialId],
            laboratory_id: LaboratoryId
    ) -> List[MaterialBalance]:
        pass