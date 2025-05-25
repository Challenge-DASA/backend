class DomainError(Exception):
    pass

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