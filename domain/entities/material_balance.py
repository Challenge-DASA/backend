import datetime
from dataclasses import dataclass

from domain.entities.material import MaterialId
from domain.exceptions import InsufficientStockError, InvalidReservationError, InvalidQuantityError
from domain.value_objects.ids import LaboratoryId


@dataclass
class MaterialBalance:
    material_id: MaterialId
    laboratory_id: LaboratoryId
    current_stock: int
    reserved_stock: int
    last_updated: datetime.datetime

    def available_stock(self) -> int:
        return self.current_stock - self.reserved_stock

    def can_reserve(self, quantity: int) -> bool:
        return self.available_stock() >= quantity > 0

    def reserve(self, quantity: int) -> None:
        if not self.can_reserve(quantity):
            raise InsufficientStockError(
                f"Cannot reserve {quantity} of material {self.material_id}. "
                f"Available: {self.available_stock()}"
            )
        self.reserved_stock += quantity
        self.last_updated = datetime.datetime.now(datetime.UTC)

    def consume_reservation(self, quantity: int) -> None:
        if self.reserved_stock < quantity:
            raise InvalidReservationError(
                f"Cannot consume {quantity} reserved items. "
                f"Reserved: {self.reserved_stock}"
            )
        self.reserved_stock -= quantity
        self.current_stock -= quantity
        self.last_updated = datetime.datetime.now(datetime.UTC)

    def release_reservation(self, quantity: int) -> None:
        if self.reserved_stock < quantity:
            raise InvalidReservationError(
                f"Cannot release {quantity} reserved items. "
                f"Reserved: {self.reserved_stock}"
            )
        self.reserved_stock -= quantity
        self.last_updated = datetime.datetime.now(datetime.UTC)

    def add_stock(self, quantity: int) -> None:
        if quantity <= 0:
            raise InvalidQuantityError("Quantity must be positive")
        self.current_stock += quantity
        self.last_updated = datetime.datetime.now(datetime.UTC)

    def has_sufficient_stock(self, required_quantity: int) -> bool:
        return self.available_stock() >= required_quantity