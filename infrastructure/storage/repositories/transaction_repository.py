from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from domain.entities.transaction import Transaction
from domain.repositories.transaction import TransactionRepository
from domain.value_objects.ids import TransactionId
from infrastructure.storage.mappers.transaction import TransactionMapper, TransactionItemMapper
from infrastructure.storage.models.transaction import TransactionModel


class TransactionRepositoryImpl(TransactionRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, transaction: Transaction) -> None:
        transaction_model = TransactionMapper.to_model(transaction)

        existing = await self.session.get(TransactionModel, transaction.transaction_id.value.bytes)

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
            .where(TransactionModel.transaction_id == transaction_id.value.bytes)
        )

        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        return TransactionMapper.to_domain(model) if model else None

    async def exists(self, transaction_id: TransactionId) -> bool:
        stmt = select(TransactionModel.transaction_id).where(
            TransactionModel.transaction_id == transaction_id.value.bytes
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None