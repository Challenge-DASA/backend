from abc import ABC, abstractmethod
from typing import Optional, List

from domain.entities.material_balance import MaterialBalance
from domain.value_objects.ids import MaterialId, LaboratoryId


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
    async def find_multiple_by_laboratory(
            self,
            material_ids: List[MaterialId],
            laboratory_id: LaboratoryId
    ) -> List[MaterialBalance]:
        pass