import uuid
import datetime

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.oracle import RAW
from sqlalchemy.orm import relationship

from storage.models.base import Base


class TransactionModel(Base):
    __tablename__ = 'transactions'

    transaction_id = Column(RAW(16), primary_key=True, default=lambda: uuid.uuid4().bytes)
    transaction_type = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False)
    laboratory_id = Column(RAW(16), nullable=False)
    user_id = Column(RAW(16), nullable=False)
    procedure_id = Column(RAW(16), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC), nullable=False)
    authorized_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    items = relationship("TransactionItemModel", back_populates="transaction")


class TransactionItemModel(Base):
    __tablename__ = 'transaction_items'

    transaction_id = Column(RAW(16), ForeignKey('transactions.transaction_id'), primary_key=True)
    material_id = Column(RAW(16), primary_key=True)
    dispenser_id = Column(RAW(16), nullable=False)
    quantity = Column(Integer, nullable=False)

    transaction = relationship("TransactionModel", back_populates="items")