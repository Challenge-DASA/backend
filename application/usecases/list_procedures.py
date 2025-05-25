from application.dto.input.procedure import ListProceduresInput
from application.dto.output.procedure import ListProceduresOutput, ProcedureOutput
from domain.repositories.procedure import ProcedureRepository
from domain.value_objects.ids import LaboratoryId


class ListProceduresUseCase:
    def __init__(self, procedure_repository: ProcedureRepository):
        self.procedure_repository = procedure_repository

    async def execute(self, input_data: ListProceduresInput) -> ListProceduresOutput:
        laboratory_id = LaboratoryId.from_string(input_data.laboratory_id)

        procedures = await self.procedure_repository.find_by_laboratory(laboratory_id)

        procedure_outputs = [
            ProcedureOutput(
                id=str(procedure.procedure_id.value),
                name=procedure.name,
                description=procedure.description,
                created_at=procedure.created_at,
                updated_at=procedure.updated_at
            )
            for procedure in procedures
        ]

        return ListProceduresOutput(
            procedures=procedure_outputs,
            total_count=len(procedure_outputs)
        )