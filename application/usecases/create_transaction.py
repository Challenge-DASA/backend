from domain.context import Context
from domain.entities.laboratory import LaboratoryId
from domain.entities.procedure import ProcedureId

class WithdrawTransaction:
    def execute(self, context: Context, laboratory_id: LaboratoryId, medical_procedure_id: ProcedureId) -> dict:
        return None