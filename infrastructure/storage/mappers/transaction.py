from domain.entities.transaction import Transaction, TransactionItem
from domain.value_objects.ids import *
from domain.value_objects.enums import TransactionType, TransactionStatus
from infrastructure.storage.models.transaction import TransactionModel, TransactionItemModel
import uuid


class TransactionMapper:

    @staticmethod
    def to_domain(model: TransactionModel) -> Transaction:
        return Transaction(
            transaction_id=TransactionId(uuid.UUID(bytes=model.transaction_id)),
            transaction_type=TransactionType(model.transaction_type),
            status=TransactionStatus(model.status),
            laboratory_id=LaboratoryId(uuid.UUID(bytes=model.laboratory_id)),
            user_id=UserId(uuid.UUID(bytes=model.user_id)),
            procedure_id=ProcedureId(uuid.UUID(bytes=model.procedure_id)) if model.procedure_id else None,
            created_at=model.created_at,
            authorized_at=model.authorized_at,
            completed_at=model.completed_at,
            items=[TransactionItemMapper.to_domain(item) for item in model.items]
        )

    @staticmethod
    def to_model(entity: Transaction) -> TransactionModel:
        return TransactionModel(
            transaction_id=entity.transaction_id.value.bytes,
            transaction_type=entity.transaction_type.value,
            status=entity.status.value,
            laboratory_id=entity.laboratory_id.value.bytes,
            user_id=entity.user_id.value.bytes,
            procedure_id=entity.procedure_id.value.bytes if entity.procedure_id else None,
            created_at=entity.created_at,
            authorized_at=entity.authorized_at,
            completed_at=entity.completed_at
        )


class TransactionItemMapper:

    @staticmethod
    def to_domain(model: TransactionItemModel) -> TransactionItem:
        return TransactionItem(
            material_id=MaterialId(uuid.UUID(bytes=model.material_id)),
            quantity=model.quantity
        )

    @staticmethod
    def to_model(entity: TransactionItem, transaction_id: TransactionId) -> TransactionItemModel:
        return TransactionItemModel(
            transaction_id=transaction_id.value.bytes,
            material_id=entity.material_id.value.bytes,
            quantity=entity.quantity
        )