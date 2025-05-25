from typing import List, Dict
from dataclasses import dataclass


class ApplicationError(Exception):
    def __init__(self, message: str, details: Dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ProcedureNotFoundError(ApplicationError):
    def __init__(self, procedure_id: str):
        super().__init__(
            message=f"Procedure {procedure_id} not found or inactive",
            details={"procedure_id": procedure_id}
        )


class ProcedureNotAvailableInLaboratoryError(ApplicationError):
    def __init__(self, procedure_id: str, laboratory_id: str):
        super().__init__(
            message=f"Procedure {procedure_id} not available in laboratory {laboratory_id}",
            details={
                "procedure_id": procedure_id,
                "laboratory_id": laboratory_id
            }
        )


class NoMaterialsDefinedError(ApplicationError):
    def __init__(self, procedure_id: str):
        super().__init__(
            message=f"No materials defined for procedure {procedure_id}",
            details={"procedure_id": procedure_id}
        )


@dataclass
class MaterialStockInfo:
    material_id: str
    required: int
    available: int


class InsufficientMaterialsError(ApplicationError):
    def __init__(self, material_details: List[MaterialStockInfo]):
        count = len(material_details)
        super().__init__(
            message=f"{count} material{'s' if count > 1 else ''} with insufficient stock",
            details={
                "materials": [
                    {
                        "material_id": detail.material_id,
                        "required": detail.required,
                        "available": detail.available
                    }
                    for detail in material_details
                ],
                "count": count
            }
        )


class MaterialReservationError(ApplicationError):
    def __init__(self, original_error: str, materials_attempted: List[str] = None):
        super().__init__(
            message=f"Failed to reserve materials: {original_error}",
            details={
                "original_error": original_error,
                "materials_attempted": materials_attempted or []
            }
        )


class TransactionCreationError(ApplicationError):
    def __init__(self, original_error: str, transaction_data: Dict = None):
        super().__init__(
            message=f"Failed to create transaction: {original_error}",
            details={
                "original_error": original_error,
                "transaction_data": transaction_data or {}
            }
        )