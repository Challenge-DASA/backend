from dataclasses import dataclass

from domain.exceptions import InvalidProcedureCountError
from domain.value_objects.ids import MaterialId, ProcedureId


@dataclass
class ProcedureUsage:
    procedure_id: ProcedureId
    material_id: MaterialId
    required_amount: int

    def is_valid_requirement(self) -> bool:
        return self.required_amount > 0

    def calculate_total_for_procedures(self, procedure_count: int) -> int:
        if procedure_count <= 0:
            raise InvalidProcedureCountError()
        return self.required_amount * procedure_count
