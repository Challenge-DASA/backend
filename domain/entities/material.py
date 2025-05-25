import datetime
from dataclasses import dataclass
from typing import Optional

from domain.exceptions import MaterialNotDeletedError, MaterialAlreadyDeletedError
from domain.value_objects.ids import MaterialId


@dataclass
class Material:
    id: MaterialId
    name: str
    description: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    is_deleted: bool = False
    deleted_at: Optional[datetime.datetime] = None

    def update_info(self, name: str, description: str) -> None:
        self.name = name
        self.description = description
        self.updated_at = datetime.datetime.now(datetime.UTC)

    def soft_delete(self) -> None:
        if self.is_deleted:
            raise MaterialAlreadyDeletedError()
        self.is_deleted = True
        self.deleted_at = datetime.datetime.now(datetime.UTC)
        self.updated_at = datetime.datetime.now(datetime.UTC)

    def restore(self) -> None:
        if not self.is_deleted:
            raise MaterialNotDeletedError()
        self.is_deleted = False
        self.deleted_at = None
        self.updated_at = datetime.datetime.now(datetime.UTC)

    def is_active(self) -> bool:
        return not self.is_deleted