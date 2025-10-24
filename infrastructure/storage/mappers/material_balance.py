import uuid

from domain.entities.material_balance import MaterialBalance
from domain.value_objects.ids import MaterialId, LaboratoryId
from infrastructure.storage.models.material_balance import MaterialBalanceModel


class MaterialBalanceMapper:

    @staticmethod
    def to_domain(model: MaterialBalanceModel) -> MaterialBalance:
        # asyncpg já retorna UUID nativo do Python
        material_id = model.material_id
        if not isinstance(material_id, uuid.UUID):
            material_id = uuid.UUID(str(material_id))

        laboratory_id = model.laboratory_id
        if not isinstance(laboratory_id, uuid.UUID):
            laboratory_id = uuid.UUID(str(laboratory_id))

        return MaterialBalance(
            material_id=MaterialId(material_id),
            laboratory_id=LaboratoryId(laboratory_id),
            current_stock=model.current_stock,
            reserved_stock=model.reserved_stock,
            last_updated=model.last_updated
        )

    @staticmethod
    def to_model(entity: MaterialBalance) -> MaterialBalanceModel:
        return MaterialBalanceModel(
            material_id=entity.material_id.value,  # Passa o UUID diretamente
            laboratory_id=entity.laboratory_id.value,  # Passa o UUID diretamente
            current_stock=entity.current_stock,
            reserved_stock=entity.reserved_stock,
            last_updated=entity.last_updated
        )