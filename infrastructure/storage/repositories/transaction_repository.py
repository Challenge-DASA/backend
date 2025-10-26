import datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from domain.entities.transaction import Transaction
from domain.repositories.transaction import TransactionRepository
from domain.value_objects.ids import TransactionId, LaboratoryId, UserId
from domain.value_objects.enums import TransactionType, TransactionStatus
from infrastructure.storage.mappers.transaction import TransactionMapper, TransactionItemMapper
from infrastructure.storage.models.transaction import TransactionModel


class TransactionRepositoryImpl(TransactionRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, transaction: Transaction) -> None:
        transaction_model = TransactionMapper.to_model(transaction)

        existing = await self.session.get(TransactionModel, transaction.transaction_id.value)

        if existing:
            existing.status = transaction_model.status
            existing.authorized_at = transaction_model.authorized_at
            existing.completed_at = transaction_model.completed_at
        else:
            self.session.add(transaction_model)

            for item in transaction.items:
                item_model = TransactionItemMapper.to_model(item, transaction.transaction_id)
                self.session.add(item_model)

        await self.session.commit()

    async def find_by_id(self, transaction_id: TransactionId) -> Optional[Transaction]:
        stmt = (
            select(TransactionModel)
            .options(selectinload(TransactionModel.items))
            .where(TransactionModel.transaction_id == transaction_id.value)
        )

        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        return TransactionMapper.to_domain(model) if model else None

    async def exists(self, transaction_id: TransactionId) -> bool:
        stmt = select(TransactionModel.transaction_id).where(
            TransactionModel.transaction_id == transaction_id.value
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def find_with_filters(
        self,
        laboratory_id: Optional[LaboratoryId] = None,
        user_id: Optional[UserId] = None,
        transaction_type: Optional[TransactionType] = None,
        status: Optional[TransactionStatus] = None,
        start_date: Optional[datetime.datetime] = None,
        end_date: Optional[datetime.datetime] = None
    ) -> List[Transaction]:
        """
        Busca transações com filtros opcionais.
        Todos os filtros são aplicados como AND.
        """
        # Monta a query base com eager loading dos items
        stmt = (
            select(TransactionModel)
            .options(selectinload(TransactionModel.items))
        )

        # Lista de condições para o WHERE
        conditions = []

        # Aplica filtros se fornecidos
        if laboratory_id:
            conditions.append(TransactionModel.laboratory_id == laboratory_id.value)

        if user_id:
            conditions.append(TransactionModel.user_id == user_id.value)

        if transaction_type:
            conditions.append(TransactionModel.transaction_type == transaction_type.value)

        if status:
            conditions.append(TransactionModel.status == status.value)

        if start_date:
            conditions.append(TransactionModel.created_at >= start_date)

        if end_date:
            conditions.append(TransactionModel.created_at <= end_date)

        # Aplica todas as condições com AND
        if conditions:
            stmt = stmt.where(and_(*conditions))

        # Ordena por data de criação (mais recentes primeiro)
        stmt = stmt.order_by(TransactionModel.created_at.desc())

        # Executa query
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        # Converte para domínio
        return [TransactionMapper.to_domain(model) for model in models]