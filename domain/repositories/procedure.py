from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.procedure import ProcedureUsage, Procedure
from domain.value_objects.ids import ProcedureId


class ProcedureRepository(ABC):

    @abstractmethod
    async def find_by_id(self, procedure_id: ProcedureId) -> Optional[Procedure]:
        pass

    @abstractmethod
    async def find_required_materials(
            self,
            procedure_id: ProcedureId
    ) -> List[ProcedureUsage]:
        pass

    @abstractmethod
    async def exists(self, procedure_id: ProcedureId) -> bool:
        pass