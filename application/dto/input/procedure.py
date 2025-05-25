from dataclasses import dataclass


@dataclass(frozen=True)
class ListProceduresInput:
    laboratory_id: str

@dataclass(frozen=True)
class ListProcedureMaterialsInput:
    procedure_id: str