from application.dto.input.procedure import ListProcedureMaterialsInput
from application.dto.output.procedure import ListProcedureMaterialsOutput, ProcedureMaterialOutput
from domain.repositories.material import MaterialRepository
from domain.repositories.procedure import ProcedureRepository
from domain.value_objects.ids import ProcedureId


class ListProcedureMaterialsUseCase:

    def __init__(self, procedure_repository: ProcedureRepository, material_repository: MaterialRepository):
        self.procedure_repository = procedure_repository
        self.material_repository = material_repository

    async def execute(self, input_data: ListProcedureMaterialsInput) -> ListProcedureMaterialsOutput:
        procedure_id = ProcedureId.from_string(input_data.procedure_id)

        procedure = await self.procedure_repository.find_by_id(procedure_id)
        if not procedure:
            raise ValueError(f"Procedure {input_data.procedure_id} not found")

        procedure_materials = await self.procedure_repository.find_required_materials(procedure_id)
        if not procedure_materials:
            raise ValueError(f"No materials found for procedure {input_data.procedure_id}")

        material_ids = [material.material_id for material in procedure_materials]

        required_amounts_map = {
            procedure_material.material_id: procedure_material.required_amount
            for procedure_material in procedure_materials
        }

        materials = await self.material_repository.find_by_multiple_ids(material_ids)

        material_outputs = []
        for material in materials:
            if material.is_active():
                material_output = ProcedureMaterialOutput(
                    id=str(material.id.value),
                    name=material.name,
                    description=material.description,
                    required_amount=required_amounts_map[material.id],
                )
                material_outputs.append(material_output)

        return ListProcedureMaterialsOutput(
            materials=material_outputs,
            total_materials=len(material_outputs),
        )