from domain.entities.transaction import Transaction, TransactionItem
from domain.value_objects.ids import *
from domain.value_objects.enums import TransactionType, TransactionStatus
from infrastructure.storage.models.transaction import TransactionModel, TransactionItemModel
import uuid


class TransactionMapper:

    @staticmethod
    def to_domain(model: TransactionModel) -> Transaction:
        # asyncpg já retorna UUID nativo do Python
        transaction_id = model.transaction_id
        if not isinstance(transaction_id, uuid.UUID):
            transaction_id = uuid.UUID(str(transaction_id))

        laboratory_id = model.laboratory_id
        if not isinstance(laboratory_id, uuid.UUID):
            laboratory_id = uuid.UUID(str(laboratory_id))

        user_id = model.user_id
        if not isinstance(user_id, uuid.UUID):
            user_id = uuid.UUID(str(user_id))

        procedure_id = None
        if model.procedure_id:
            procedure_id = model.procedure_id
            if not isinstance(procedure_id, uuid.UUID):
                procedure_id = uuid.UUID(str(procedure_id))
            procedure_id = ProcedureId(procedure_id)

        return Transaction(
            transaction_id=TransactionId(transaction_id),
            transaction_type=TransactionType(model.transaction_type),
            status=TransactionStatus(model.status),
            laboratory_id=LaboratoryId(laboratory_id),
            user_id=UserId(user_id),
            procedure_id=procedure_id,
            created_at=model.created_at,
            authorized_at=model.authorized_at,
            completed_at=model.completed_at,
            items=[TransactionItemMapper.to_domain(item) for item in model.items]
        )

    @staticmethod
    def to_model(entity: Transaction) -> TransactionModel:
        return TransactionModel(
            transaction_id=entity.transaction_id.value,  # Passa o UUID diretamente
            transaction_type=entity.transaction_type.value,
            status=entity.status.value,
            laboratory_id=entity.laboratory_id.value,  # Passa o UUID diretamente
            user_id=entity.user_id.value,  # Passa o UUID diretamente
            procedure_id=entity.procedure_id.value if entity.procedure_id else None,  # Passa o UUID diretamente
            created_at=entity.created_at,
            authorized_at=entity.authorized_at,
            completed_at=entity.completed_at
        )


class TransactionItemMapper:

    @staticmethod
    def to_domain(model: TransactionItemModel) -> TransactionItem:
        # asyncpg já retorna UUID nativo do Python
        material_id = model.material_id
        if not isinstance(material_id, uuid.UUID):
            material_id = uuid.UUID(str(material_id))

        return TransactionItem(
            material_id=MaterialId(material_id),
            quantity=model.quantity
        )

    @staticmethod
    def to_model(entity: TransactionItem, transaction_id: TransactionId) -> TransactionItemModel:
        return TransactionItemModel(
            transaction_id=transaction_id.value,  # Passa o UUID diretamente
            material_id=entity.material_id.value,  # Passa o UUID diretamente
            quantity=entity.quantity
        )