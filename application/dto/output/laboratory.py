from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass(frozen=True)
class MaterialBalanceOutput:
    material_id: str
    material_name: str
    material_description: str
    current_stock: int
    reserved_stock: int
    available_stock: int
    last_updated: datetime


@dataclass(frozen=True)
class ListLaboratoryBalanceOutput:
    materials: List[MaterialBalanceOutput]
    total_materials: int
