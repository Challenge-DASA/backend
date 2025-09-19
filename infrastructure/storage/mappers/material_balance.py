import uuid

from domain.entities.material_balance import MaterialBalance
from domain.value_objects.ids import MaterialId, LaboratoryId
from infrastructure.storage.models.material_balance import MaterialBalanceModel


class MaterialBalanceMapper:

    @staticmethod
    def to_domain(model: MaterialBalanceModel) -> MaterialBalance:
        return MaterialBalance(
            material_id=MaterialId(uuid.UUID(bytes=model.material_id)),
            laboratory_id=LaboratoryId(uuid.UUID(bytes=model.laboratory_id)),
            current_stock=model.current_stock,
            reserved_stock=model.reserved_stock,
            last_updated=model.last_updated
        )

    @staticmethod
    def to_model(entity: MaterialBalance) -> MaterialBalanceModel:
        return MaterialBalanceModel(
            material_id=entity.material_id.value.bytes,
            laboratory_id=entity.laboratory_id.value.bytes,
            current_stock=entity.current_stock,
            reserved_stock=entity.reserved_stock,
            last_updated=entity.last_updated
        )