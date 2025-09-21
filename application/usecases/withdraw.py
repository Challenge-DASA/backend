import datetime
import logging
import uuid
from uuid import uuid4
from typing import List, Dict

from application.dto.input.transaction import WithdrawTransactionInput
from application.dto.output.transaction import WithdrawTransactionOutput, TransactionItemOutput
from application.exceptions import (
    ProcedureNotFoundError,
    ProcedureNotAvailableInLaboratoryError,
    NoMaterialsDefinedError,
    InsufficientMaterialsError,
    MaterialReservationError,
    TransactionCreationError,
    MaterialStockInfo
)

from domain.context import Context
from domain.entities.procedure_usage import ProcedureUsage
from domain.entities.transaction_item import TransactionItem
from domain.entities.transaction import Transaction
from domain.entities.procedure import Procedure
from domain.entities.material_balance import MaterialBalance
from domain.repositories.material import MaterialBalanceRepository, MaterialRepository
from domain.repositories.procedure import ProcedureRepository
from domain.repositories.transaction import TransactionRepository
from domain.value_objects.enums import TransactionType, TransactionStatus
from domain.value_objects.ids import LaboratoryId, ProcedureId, TransactionId, MaterialId, UserId

logger = logging.getLogger(__name__)


class WithdrawTransactionUseCase:
    def __init__(
            self,
            transaction_repository: TransactionRepository,
            procedure_repository: ProcedureRepository,
            material_balance_repository: MaterialBalanceRepository,
            material_repository: MaterialRepository
    ):
        self.transaction_repository = transaction_repository
        self.procedure_repository = procedure_repository
        self.material_balance_repository = material_balance_repository
        self.material_repository = material_repository

    async def execute(self, context: Context, input_data: WithdrawTransactionInput) -> WithdrawTransactionOutput:
        laboratory_id = LaboratoryId.from_string(input_data.laboratory_id)
        procedure_id = ProcedureId.from_string(input_data.procedure_id)
        user_id = UserId.from_string(str(context.user_id))

        await self._validate_procedure_exists(procedure_id)
        slot_id = await self._validate_procedure_available_in_laboratory(procedure_id, laboratory_id)
        procedure_materials = await self._get_required_materials(procedure_id)
        material_balances = await self._validate_stock_availability(procedure_materials, laboratory_id)
        await self._reserve_materials(material_balances, procedure_materials)

        transaction_items = await self._create_transaction_items(procedure_materials)
        transaction = self._create_transaction(
            laboratory_id, procedure_id, user_id, transaction_items
        )
        await self._save_transaction(transaction)

        await self._execute_dispensation_commands(procedure_id, slot_id)

        return self._build_output(transaction)

    async def _validate_procedure_exists(self, procedure_id: ProcedureId) -> Procedure:
        procedure = await self.procedure_repository.find_by_id(procedure_id)
        if not procedure or not procedure.is_active():
            raise ProcedureNotFoundError(str(procedure_id.value))
        return procedure

    async def _validate_procedure_available_in_laboratory(
            self,
            procedure_id: ProcedureId,
            laboratory_id: LaboratoryId
    ) -> int:
        lab_procedures = await self.procedure_repository.find_by_laboratory_procedure(laboratory_id)

        for p in lab_procedures:
            if p.laboratory_id == laboratory_id and procedure_id == p.procedure_id:
                return p.slot_id

        raise ProcedureNotAvailableInLaboratoryError(
            str(procedure_id.value),
            str(laboratory_id.value)
        )

    async def _get_required_materials(self, procedure_id: ProcedureId) -> List[ProcedureUsage]:
        procedure_materials = await self.procedure_repository.find_required_materials(procedure_id)
        if not procedure_materials:
            raise NoMaterialsDefinedError(str(procedure_id.value))
        return procedure_materials

    async def _validate_stock_availability(
            self,
            procedure_materials: List[ProcedureUsage],
            laboratory_id: LaboratoryId
    ) -> Dict[MaterialId, MaterialBalance]:
        material_ids = [pm.material_id for pm in procedure_materials]
        material_balances = await self.material_balance_repository.find_multiple_by_laboratory(
            material_ids, laboratory_id
        )

        balances_map = {balance.material_id: balance for balance in material_balances}
        required_amounts_map = {pm.material_id: pm.required_amount for pm in procedure_materials}

        insufficient_materials = []
        for material_id, required_amount in required_amounts_map.items():
            balance = balances_map.get(material_id)
            if not balance:
                insufficient_materials.append(MaterialStockInfo(
                    material_id=str(material_id.value),
                    required=required_amount,
                    available=0
                ))
            elif not balance.has_sufficient_stock(required_amount):
                available = balance.available_stock()
                insufficient_materials.append(MaterialStockInfo(
                    material_id=str(material_id.value),
                    required=required_amount,
                    available=available
                ))

        if insufficient_materials:
            raise InsufficientMaterialsError(insufficient_materials)

        return balances_map

    async def _reserve_materials(
            self,
            balances_map: Dict[MaterialId, MaterialBalance],
            procedure_materials: List[ProcedureUsage]
    ) -> None:
        required_amounts_map = {pm.material_id: pm.required_amount for pm in procedure_materials}
        materials_attempted = []

        try:
            for material_id, required_amount in required_amounts_map.items():
                materials_attempted.append(str(material_id.value))
                balance = balances_map[material_id]
                balance.reserve(required_amount)
                await self.material_balance_repository.save(balance)
        except Exception as e:
            # TODO: Implementar rollback das reservas já feitas
            raise MaterialReservationError(str(e), materials_attempted)

    async def _create_transaction_items(self, procedure_materials: List[ProcedureUsage]) -> List[TransactionItem]:
        material_ids = [pm.material_id for pm in procedure_materials]
        materials = await self.material_repository.find_by_multiple_ids(material_ids)
        materials_map = {material.id: material for material in materials}
        required_amounts_map = {pm.material_id: pm.required_amount for pm in procedure_materials}

        transaction_items = []
        for material_id, required_amount in required_amounts_map.items():
            material = materials_map.get(material_id)
            if material and material.is_active():
                transaction_items.append(
                    TransactionItem(
                        material_id=material_id,
                        quantity=required_amount
                    )
                )

        return transaction_items

    @staticmethod
    def _create_transaction(
            laboratory_id: LaboratoryId,
            procedure_id: ProcedureId,
            user_id,
            transaction_items: List[TransactionItem]
    ) -> Transaction:
        now = datetime.datetime.now(datetime.UTC)

        return Transaction(
            transaction_id=TransactionId(uuid4()),
            transaction_type=TransactionType.WITHDRAW,
            status=TransactionStatus.AUTHORIZED,
            laboratory_id=laboratory_id,
            user_id=user_id,
            procedure_id=procedure_id,
            created_at=now,
            authorized_at=now,
            completed_at=None,
            items=transaction_items
        )

    async def _save_transaction(self, transaction: Transaction) -> None:
        try:
            await self.transaction_repository.save(transaction)
        except Exception as e:
            raise TransactionCreationError(
                str(e),
                {
                    "transaction_id": str(transaction.transaction_id.value),
                    "laboratory_id": str(transaction.laboratory_id.value),
                    "procedure_id": str(transaction.procedure_id.value)
                }
            )

    async def _execute_dispensation_commands(self, procedure_id: ProcedureId, procedure_slot: int) -> None:
        from infrastructure.mqtt.integration import send_device_command

        device_id = "smartlab_001"

        success = send_device_command(device_id, "withdraw", slot=procedure_slot)

        if success:
            logger.info(f"Comando de dispensação enviado para procedimento {procedure_id.value}, slot {procedure_slot}")
        else:
            logger.error(f"Falha ao enviar comando para procedimento {procedure_id.value}, slot {procedure_slot}")

    def _get_procedure_slot(self, procedure_id: ProcedureId) -> int:
        return int(str(procedure_id.value)[-1]) + 1

    @staticmethod
    def _build_output(transaction: Transaction) -> WithdrawTransactionOutput:
        return WithdrawTransactionOutput(
            transaction_id=str(transaction.transaction_id.value),
            transaction_type=transaction.transaction_type.value,
            status=transaction.status.value,
            laboratory_id=str(transaction.laboratory_id.value),
            procedure_id=str(transaction.procedure_id.value),
            created_at=transaction.created_at,
            authorized_at=transaction.authorized_at,
            items=[
                TransactionItemOutput(
                    material_id=str(item.material_id.value),
                    quantity=item.quantity
                )
                for item in transaction.items
            ],
        )