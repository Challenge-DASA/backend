import datetime
import uuid

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from infrastructure.storage.models.base import Base, SoftDeleteMixin


class ProcedureModel(Base, SoftDeleteMixin):
    __tablename__ = 'procedures'

    procedure_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC), nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC), onupdate=datetime.datetime.now(datetime.UTC), nullable=False)


class ProcedureUsageModel(Base):
    __tablename__ = 'procedure_usages'

    procedure_id = Column(UUID(as_uuid=True), ForeignKey('procedures.procedure_id'), primary_key=True)
    material_id = Column(UUID(as_uuid=True), ForeignKey('materials.material_id'), primary_key=True)
    required_amount = Column(Integer, nullable=False)


class LaboratoryProcedureModel(Base):
    __tablename__ = 'laboratory_procedures'

    laboratory_id = Column(UUID(as_uuid=True), primary_key=True)
    procedure_id = Column(UUID(as_uuid=True), ForeignKey('procedures.procedure_id'), primary_key=True)
    slot = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC), nullable=False)

    procedure = relationship("ProcedureModel")