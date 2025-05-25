from dataclasses import dataclass

from domain.value_objects.ids import MaterialId


@dataclass(frozen=True)
class TransactionItem:
    material_id: MaterialId
    quantity: int

    def is_valid(self) -> bool:
        return self.quantity > 0