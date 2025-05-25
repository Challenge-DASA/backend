import datetime
import uuid

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.oracle import RAW

from storage.models.base import SoftDeleteMixin, Base


class MaterialModel(Base, SoftDeleteMixin):
    __tablename__ = 'materials'

    material_id = Column(RAW(16), primary_key=True, default=lambda: uuid.uuid4().bytes)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC), nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC), onupdate=datetime.datetime.now(datetime.UTC), nullable=False)