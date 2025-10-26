import datetime

from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID

from infrastructure.storage.models.base import Base


class MaterialBalanceModel(Base):
    __tablename__ = 'material_balances'

    material_id = Column(UUID(as_uuid=True), primary_key=True)
    laboratory_id = Column(UUID(as_uuid=True), primary_key=True)
    current_stock = Column(Integer, nullable=False, default=0)
    reserved_stock = Column(Integer, nullable=False, default=0)
    last_updated = Column(DateTime(timezone=True), default=datetime.datetime.now(datetime.UTC), nullable=False)
