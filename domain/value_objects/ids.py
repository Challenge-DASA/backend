from dataclasses import dataclass
from uuid import UUID

from domain.exceptions import InvalidResourceIdError


@dataclass(frozen=True)
class TransactionId:
    value: UUID

    @classmethod
    def from_string(cls, id_str: str) -> 'TransactionId':
        if not id_str or not id_str.strip():
            raise InvalidResourceIdError(
                "Transaction ID string cannot be empty or null",
                field="transaction_id",
                invalid_value=id_str
            )

        try:
            uuid_value = UUID(id_str.strip())
            return cls(value=uuid_value)
        except ValueError as e:
            raise InvalidResourceIdError(
                "Invalid transaction ID format",
                field="transaction_id",
                invalid_value=id_str
            ) from e


@dataclass(frozen=True)
class MaterialId:
    value: UUID

    @classmethod
    def from_string(cls, id_str: str) -> 'MaterialId':
        if not id_str or not id_str.strip():
            raise InvalidResourceIdError(
                "Material ID string cannot be empty or null",
                field="material_id",
                invalid_value=id_str
            )

        try:
            uuid_value = UUID(id_str.strip())
            return cls(value=uuid_value)
        except ValueError as e:
            raise InvalidResourceIdError(
                "Invalid material ID format",
                field="material_id",
                invalid_value=id_str
            ) from e


@dataclass(frozen=True)
class LaboratoryId:
    value: UUID

    @classmethod
    def from_string(cls, id_str: str) -> 'LaboratoryId':
        if not id_str or not id_str.strip():
            raise InvalidResourceIdError(
                "Laboratory ID string cannot be empty or null",
                field="laboratory_id",
                invalid_value=id_str
            )

        try:
            uuid_value = UUID(id_str.strip())
            return cls(value=uuid_value)
        except ValueError as e:
            raise InvalidResourceIdError(
                "Invalid laboratory ID format",
                field="laboratory_id",
                invalid_value=id_str
            ) from e


@dataclass(frozen=True)
class ProcedureId:
    value: UUID

    @classmethod
    def from_string(cls, id_str: str) -> 'ProcedureId':
        if not id_str or not id_str.strip():
            raise InvalidResourceIdError(
                "Procedure ID string cannot be empty or null",
                field="procedure_id",
                invalid_value=id_str
            )

        try:
            uuid_value = UUID(id_str.strip())
            return cls(value=uuid_value)
        except ValueError as e:
            raise InvalidResourceIdError(
                "Invalid procedure ID format",
                field="procedure_id",
                invalid_value=id_str
            ) from e


@dataclass(frozen=True)
class UserId:
    value: UUID

    @classmethod
    def from_string(cls, id_str: str) -> 'UserId':
        if not id_str or not id_str.strip():
            raise InvalidResourceIdError(
                "User ID string cannot be empty or null",
                field="user_id",
                invalid_value=id_str
            )

        try:
            uuid_value = UUID(id_str.strip())
            return cls(value=uuid_value)
        except ValueError as e:
            raise InvalidResourceIdError(
                "Invalid user ID format",
                field="user_id",
                invalid_value=id_str
            ) from e


@dataclass(frozen=True)
class DispenserId:
    value: UUID

    @classmethod
    def from_string(cls, id_str: str) -> 'DispenserId':
        if not id_str or not id_str.strip():
            raise InvalidResourceIdError(
                "Dispenser ID string cannot be empty or null",
                field="dispenser_id",
                invalid_value=id_str
            )

        try:
            uuid_value = UUID(id_str.strip())
            return cls(value=uuid_value)
        except ValueError as e:
            raise InvalidResourceIdError(
                "Invalid dispenser ID format",
                field="dispenser_id",
                invalid_value=id_str
            ) from e