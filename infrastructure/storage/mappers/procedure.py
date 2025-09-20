import uuid
from domain.entities.procedure import Procedure, LaboratoryProcedure
from domain.entities.procedure_usage import ProcedureUsage
from domain.value_objects.ids import ProcedureId, MaterialId, LaboratoryId
from infrastructure.storage.models.procedure import ProcedureModel, ProcedureUsageModel, LaboratoryProcedureModel


# storage/mappers/procedure_mapper.py
class ProcedureMapper:

    @staticmethod
    def to_domain(model: ProcedureModel) -> Procedure:
        return Procedure(
            procedure_id=ProcedureId(uuid.UUID(bytes=model.procedure_id)),
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
            procedure_id=entity.procedure_id.value.bytes,
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
        return ProcedureUsage(
            procedure_id=ProcedureId(uuid.UUID(bytes=model.procedure_id)),
            material_id=MaterialId(uuid.UUID(bytes=model.material_id)),
            required_amount=model.required_amount
        )

    @staticmethod
    def to_model(entity: ProcedureUsage) -> ProcedureUsageModel:
        return ProcedureUsageModel(
            procedure_id=entity.procedure_id.value.bytes,
            material_id=entity.material_id.value.bytes,
            required_amount=entity.required_amount
        )

class LaboratoryProcedureMapper:

    @staticmethod
    def to_domain(model: LaboratoryProcedureModel) -> LaboratoryProcedure:
        return LaboratoryProcedure(
            laboratory_id=LaboratoryId(uuid.UUID(bytes=model.laboratory_id)),
            procedure_id=ProcedureId(uuid.UUID(bytes=model.procedure_id)),
            slot_id=model.slot,
            created_at=model.created_at
        )

    @staticmethod
    def to_model(entity: LaboratoryProcedure) -> LaboratoryProcedureModel:
        return LaboratoryProcedureModel(
            laboratory_id=entity.laboratory_id.value.bytes,
            procedure_id=entity.procedure_id.value.bytes,
            slot=entity.slot_id,
            created_at=entity.created_at
        )