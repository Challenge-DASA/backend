import uuid
import datetime

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from infrastructure.storage.models.base import Base


class TransactionModel(Base):
    __tablename__ = 'transactions'

    transaction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_type = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False)
    laboratory_id = Column(UUID(as_uuid=True), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    procedure_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC), nullable=False)
    authorized_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    items = relationship("TransactionItemModel", back_populates="transaction")


class TransactionItemModel(Base):
    __tablename__ = 'transaction_items'

    transaction_id = Column(UUID(as_uuid=True), ForeignKey('transactions.transaction_id'), primary_key=True)
    material_id = Column(UUID(as_uuid=True), primary_key=True)
    quantity = Column(Integer, nullable=False)

    transaction = relationship("TransactionModel", back_populates="items")