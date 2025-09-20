import datetime
from dataclasses import dataclass
from typing import Optional

from domain.exceptions import ProcedureAlreadyDeletedError
from domain.value_objects.ids import ProcedureId, LaboratoryId


@dataclass
class Procedure:
    procedure_id: ProcedureId
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None

    def update_info(self, name: str, description: str) -> None:
        self.name = name
        self.description = description
        self.updated_at = datetime.datetime.now(datetime.UTC)

    def soft_delete(self) -> None:
        if self.is_deleted:
            raise ProcedureAlreadyDeletedError()
        self.is_deleted = True
        self.deleted_at = datetime.datetime.now(datetime.UTC)
        self.updated_at = datetime.datetime.now(datetime.UTC)

    def is_active(self) -> bool:
        return not self.is_deleted

@dataclass
class LaboratoryProcedure:
    laboratory_id: LaboratoryId
    procedure_id: ProcedureId
    slot_id: int
    created_at: datetime