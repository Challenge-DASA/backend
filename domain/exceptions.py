from typing import Optional


class DomainError(Exception):
    pass

class InvalidResourceIdError(ValueError):
    def __init__(self, message: str, field: str, invalid_value: Optional[str] = None):
        super().__init__(message)
        self.field = field
        self.invalid_value = invalid_value

class InvalidTransactionStateError(DomainError):
    pass

class InsufficientStockError(DomainError):
    pass

class InvalidReservationError(DomainError):
    pass

class InvalidQuantityError(DomainError):
    pass

class MaterialAlreadyDeletedError(DomainError):
    pass

class MaterialNotDeletedError(DomainError):
    pass

class ProcedureAlreadyDeletedError(DomainError):
    pass

class InvalidProcedureCountError(DomainError):
    pass