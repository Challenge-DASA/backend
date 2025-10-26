import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, Boolean

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now(datetime.UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.now(datetime.UTC), onupdate=datetime.datetime.now(datetime.UTC), nullable=False)


class SoftDeleteMixin:
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)