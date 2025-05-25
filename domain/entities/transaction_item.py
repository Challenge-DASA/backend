from dataclasses import dataclass

from domain.value_objects.ids import MaterialId, DispenserId


@dataclass(frozen=True)
class TransactionItem:
    material_id: MaterialId
    dispenser_id: DispenserId
    quantity: int

    def is_valid(self) -> bool:
        return self.quantity > 0