import logging
from typing import List, Dict

from application.dto.input.transaction import ListTransactionsInput
from application.dto.output.transaction import ListTransactionsOutput, TransactionListItemOutput, ProcedureOutput, \
    MaterialItemOutput
from domain.context import Context
from domain.entities.transaction import Transaction
from domain.entities.procedure import Procedure
from domain.entities.material import Material
from domain.repositories.transaction import TransactionRepository
from domain.repositories.procedure import ProcedureRepository
from domain.repositories.material import MaterialRepository
from domain.value_objects.ids import LaboratoryId, UserId, ProcedureId, MaterialId
from domain.value_objects.enums import TransactionType, TransactionStatus

logger = logging.getLogger(__name__)


class ListTransactionsUseCase:
    def __init__(
            self,
            transaction_repository: TransactionRepository,
            procedure_repository: ProcedureRepository,
            material_repository: MaterialRepository
    ):
        self.transaction_repository = transaction_repository
        self.procedure_repository = procedure_repository
        self.material_repository = material_repository

    async def execute(self, context: Context, input_data: ListTransactionsInput) -> ListTransactionsOutput:
        filters = self._prepare_filters(input_data)

        transactions = await self.transaction_repository.find_with_filters(
            laboratory_id=filters.get('laboratory_id'),
            user_id=filters.get('user_id'),
            transaction_type=filters.get('transaction_type'),
            status=filters.get('status'),
            start_date=filters.get('start_date'),
            end_date=filters.get('end_date')
        )

        if not transactions:
            return ListTransactionsOutput(transactions=[])

        procedures_map = await self._load_procedures(transactions)
        materials_map = await self._load_materials(transactions)

        output_items = []
        for transaction in transactions:
            output_item = await self._build_transaction_item(
                transaction,
                procedures_map,
                materials_map
            )
            output_items.append(output_item)

        return ListTransactionsOutput(transactions=output_items)

    def _prepare_filters(self, input_data: ListTransactionsInput) -> Dict:
        filters = {}

        if input_data.laboratory_id:
            filters['laboratory_id'] = LaboratoryId.from_string(input_data.laboratory_id)

        if input_data.user_id:
            filters['user_id'] = UserId.from_string(input_data.user_id)

        if input_data.transaction_type:
            filters['transaction_type'] = TransactionType(input_data.transaction_type)

        if input_data.status:
            filters['status'] = TransactionStatus(input_data.status)

        if input_data.start_date:
            filters['start_date'] = input_data.start_date

        if input_data.end_date:
            filters['end_date'] = input_data.end_date

        return filters

    async def _load_procedures(self, transactions: List[Transaction]) -> Dict[ProcedureId, Procedure]:
        procedure_ids = list({
            t.procedure_id
            for t in transactions
            if t.procedure_id is not None
        })

        if not procedure_ids:
            return {}

        procedures = []
        for proc_id in procedure_ids:
            procedure = await self.procedure_repository.find_by_id(proc_id)
            if procedure and procedure.is_active():
                procedures.append(procedure)

        return {proc.procedure_id: proc for proc in procedures}

    async def _load_materials(self, transactions: List[Transaction]) -> Dict[MaterialId, Material]:
        material_ids = []
        for transaction in transactions:
            for item in transaction.items:
                material_ids.append(item.material_id)

        material_ids = list(set(material_ids))

        if not material_ids:
            return {}

        materials = await self.material_repository.find_by_multiple_ids(material_ids)

        return {
            mat.id: mat
            for mat in materials
            if mat.is_active()
        }

    async def _build_transaction_item(
            self,
            transaction: Transaction,
            procedures_map: Dict[ProcedureId, Procedure],
            materials_map: Dict[MaterialId, Material]
    ) -> TransactionListItemOutput:
        procedure_output = None
        if transaction.procedure_id:
            procedure = procedures_map.get(transaction.procedure_id)
            if procedure:
                procedure_materials = await self.procedure_repository.find_required_materials(
                    transaction.procedure_id
                )

                material_items = self._build_material_items(
                    procedure_materials,
                    transaction,
                    materials_map
                )

                procedure_output = ProcedureOutput(
                    id=str(procedure.procedure_id.value),
                    name=procedure.name,
                    items=material_items
                )

        return TransactionListItemOutput(
            employee_id=str(transaction.user_id.value),
            procedure=procedure_output,
            timestamp=transaction.created_at
        )

    def _build_material_items(
            self,
            procedure_materials,
            transaction: Transaction,
            materials_map: Dict[MaterialId, Material]
    ) -> List[MaterialItemOutput]:
        material_items = []

        transaction_quantities = {
            item.material_id: item.quantity
            for item in transaction.items
        }

        for proc_usage in procedure_materials:
            material = materials_map.get(proc_usage.material_id)
            if material:
                quantity = transaction_quantities.get(proc_usage.material_id, proc_usage.required_amount)

                material_items.append(MaterialItemOutput(
                    id=str(material.id.value),
                    name=material.name,
                    quantity=quantity
                ))

        return material_items