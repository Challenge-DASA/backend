from enum import Enum


class TransactionType(Enum):
    WITHDRAW = "WITHDRAW"
    DEPOSIT = "DEPOSIT"
    ADJUSTMENT = "ADJUSTMENT"

class TransactionStatus(Enum):
    AUTHORIZED = "AUTHORIZED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"