import datetime
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class ProcedureOutput:
    id: str
    name: str
    description: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

@dataclass(frozen=True)
class ListProceduresOutput:
    procedures: list[ProcedureOutput]
    total_count: int

@dataclass(frozen=True)
class ProcedureMaterialOutput:
    id: str
    name: str
    description: str
    required_amount: int

@dataclass(frozen=True)
class ListProcedureMaterialsOutput:
    materials: List[ProcedureMaterialOutput]
    total_materials: int