from dataclasses import dataclass


@dataclass(frozen=True)
class ListLaboratoryBalanceInput:
    laboratory_id: str