from dataclasses import dataclass


@dataclass(frozen=True)
class WithdrawTransactionInput:
    laboratory_id: str
    procedure_id: str