from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.procedure import Procedure
from domain.entities.procedure_usage import ProcedureUsage
from domain.value_objects.ids import ProcedureId, LaboratoryId


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

    @abstractmethod
    async def find_by_laboratory(self, laboratory_id: LaboratoryId) -> List[Procedure]:
        pass