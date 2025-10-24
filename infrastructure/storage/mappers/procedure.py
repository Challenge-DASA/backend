import uuid
from domain.entities.procedure import Procedure, LaboratoryProcedure
from domain.entities.procedure_usage import ProcedureUsage
from domain.value_objects.ids import ProcedureId, MaterialId, LaboratoryId
from infrastructure.storage.models.procedure import ProcedureModel, ProcedureUsageModel, LaboratoryProcedureModel


class ProcedureMapper:

    @staticmethod
    def to_domain(model: ProcedureModel) -> Procedure:
        # asyncpg já retorna UUID nativo do Python
        procedure_id = model.procedure_id
        if not isinstance(procedure_id, uuid.UUID):
            procedure_id = uuid.UUID(str(procedure_id))

        return Procedure(
            procedure_id=ProcedureId(procedure_id),
            name=model.name,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
            is_deleted=model.is_deleted,
            deleted_at=model.deleted_at
        )

    @staticmethod
    def to_model(entity: Procedure) -> ProcedureModel:
        return ProcedureModel(
            procedure_id=entity.procedure_id.value,  # Passa o UUID diretamente
            name=entity.name,
            description=entity.description,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            is_deleted=entity.is_deleted,
            deleted_at=entity.deleted_at
        )


class ProcedureUsageMapper:

    @staticmethod
    def to_domain(model: ProcedureUsageModel) -> ProcedureUsage:
        # asyncpg já retorna UUID nativo do Python
        procedure_id = model.procedure_id
        if not isinstance(procedure_id, uuid.UUID):
            procedure_id = uuid.UUID(str(procedure_id))

        material_id = model.material_id
        if not isinstance(material_id, uuid.UUID):
            material_id = uuid.UUID(str(material_id))

        return ProcedureUsage(
            procedure_id=ProcedureId(procedure_id),
            material_id=MaterialId(material_id),
            required_amount=model.required_amount
        )

    @staticmethod
    def to_model(entity: ProcedureUsage) -> ProcedureUsageModel:
        return ProcedureUsageModel(
            procedure_id=entity.procedure_id.value,  # Passa o UUID diretamente
            material_id=entity.material_id.value,  # Passa o UUID diretamente
            required_amount=entity.required_amount
        )


class LaboratoryProcedureMapper:

    @staticmethod
    def to_domain(model: LaboratoryProcedureModel) -> LaboratoryProcedure:
        # asyncpg já retorna UUID nativo do Python
        laboratory_id = model.laboratory_id
        if not isinstance(laboratory_id, uuid.UUID):
            laboratory_id = uuid.UUID(str(laboratory_id))

        procedure_id = model.procedure_id
        if not isinstance(procedure_id, uuid.UUID):
            procedure_id = uuid.UUID(str(procedure_id))

        return LaboratoryProcedure(
            laboratory_id=LaboratoryId(laboratory_id),
            procedure_id=ProcedureId(procedure_id),
            slot_id=model.slot,
            created_at=model.created_at
        )

    @staticmethod
    def to_model(entity: LaboratoryProcedure) -> LaboratoryProcedureModel:
        return LaboratoryProcedureModel(
            laboratory_id=entity.laboratory_id.value,  # Passa o UUID diretamente
            procedure_id=entity.procedure_id.value,  # Passa o UUID diretamente
            slot=entity.slot_id,
            created_at=entity.created_at
        )