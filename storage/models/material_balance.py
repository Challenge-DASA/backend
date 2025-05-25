import datetime

from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.dialects.oracle import RAW

from storage.models.base import Base


class MaterialBalanceModel(Base):
    __tablename__ = 'material_balances'

    material_id = Column(RAW(16), primary_key=True)
    laboratory_id = Column(RAW(16), primary_key=True)
    current_stock = Column(Integer, nullable=False, default=0)
    reserved_stock = Column(Integer, nullable=False, default=0)
    last_updated = Column(DateTime, default=datetime.datetime.now(datetime.UTC), nullable=False)