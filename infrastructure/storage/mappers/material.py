import uuid

from domain.entities.material import Material
from domain.value_objects.ids import MaterialId
from infrastructure.storage.models.material import MaterialModel


class MaterialMapper:
    @staticmethod
    def to_domain(model: MaterialModel) -> Material:
        # asyncpg já retorna UUID nativo do Python
        material_id = model.material_id
        if not isinstance(material_id, uuid.UUID):
            material_id = uuid.UUID(str(material_id))

        return Material(
            id=MaterialId(material_id),
            name=model.name,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
            is_deleted=model.is_deleted,
            deleted_at=model.deleted_at
        )

    @staticmethod
    def to_model(entity: Material) -> MaterialModel:
        return MaterialModel(
            material_id=entity.id.value,  # Passa o UUID diretamente
            name=entity.name,
            description=entity.description,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            is_deleted=entity.is_deleted,
            deleted_at=entity.deleted_at
        )