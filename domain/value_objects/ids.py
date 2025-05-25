from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class TransactionId:
    value: UUID

@dataclass(frozen=True)
class MaterialId:
    value: UUID

@dataclass(frozen=True)
class LaboratoryId:
    value: UUID

@dataclass(frozen=True)
class ProcedureId:
    value: UUID

@dataclass(frozen=True)
class UserId:
    value: UUID

@dataclass(frozen=True)
class DispenserId:
    value: UUID