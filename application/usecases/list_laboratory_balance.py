from application.dto.input.laboratory import ListLaboratoryBalanceInput
from application.dto.output.laboratory import ListLaboratoryBalanceOutput, MaterialBalanceOutput
from domain.repositories.material import MaterialBalanceRepository, MaterialRepository
from domain.value_objects.ids import LaboratoryId


class ListLaboratoryBalanceUseCase:

    def __init__(self, material_balance_repository: MaterialBalanceRepository, material_repository: MaterialRepository):
        self.material_balance_repository = material_balance_repository
        self.material_repository = material_repository

    async def execute(self, input_data: ListLaboratoryBalanceInput) -> ListLaboratoryBalanceOutput:
        laboratory_id = LaboratoryId.from_string(input_data.laboratory_id)

        material_balances = await self.material_balance_repository.find_by_laboratory(laboratory_id)

        if not material_balances:
            return ListLaboratoryBalanceOutput(
                materials=[],
                total_materials=0,
            )

        material_ids = [balance.material_id for balance in material_balances]

        materials = await self.material_repository.find_by_multiple_ids(material_ids)

        materials_map = {material.id: material for material in materials}

        material_outputs = []
        total_current = 0
        total_reserved = 0
        total_available = 0

        for balance in material_balances:
            material = materials_map.get(balance.material_id)

            if material and material.is_active():
                available_stock = balance.available_stock()

                material_outputs.append(
                    MaterialBalanceOutput(
                        material_id=str(material.id.value),
                        material_name=material.name,
                        material_description=material.description,
                        current_stock=balance.current_stock,
                        reserved_stock=balance.reserved_stock,
                        available_stock=available_stock,
                        last_updated=balance.last_updated
                    )
                )

                total_current += balance.current_stock
                total_reserved += balance.reserved_stock
                total_available += available_stock

        material_outputs.sort(key=lambda x: x.material_name)

        return ListLaboratoryBalanceOutput(
            materials=material_outputs,
            total_materials=len(material_outputs),
        )