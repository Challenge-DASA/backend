from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from domain.entities.procedure import Procedure
from domain.entities.procedure_usage import ProcedureUsage
from domain.repositories.procedure import ProcedureRepository
from domain.value_objects.ids import ProcedureId, LaboratoryId
from infrastructure.storage.models.procedure import ProcedureModel, ProcedureUsageModel, LaboratoryProcedureModel
from infrastructure.storage.mappers.procedure import ProcedureMapper, ProcedureUsageMapper


class ProcedureRepositoryImpl(ProcedureRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_id(self, procedure_id: ProcedureId) -> Optional[Procedure]:
        stmt = select(ProcedureModel).where(
            ProcedureModel.procedure_id == procedure_id.value.bytes
        )

        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        return ProcedureMapper.to_domain(model) if model else None

    async def find_required_materials(
            self,
            procedure_id: ProcedureId
    ) -> List[ProcedureUsage]:
        stmt = select(ProcedureUsageModel).where(
            ProcedureUsageModel.procedure_id == procedure_id.value.bytes
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [ProcedureUsageMapper.to_domain(model) for model in models]

    async def exists(self, procedure_id: ProcedureId) -> bool:
        stmt = select(ProcedureModel.procedure_id).where(
            ProcedureModel.procedure_id == procedure_id.value.bytes,
            ProcedureModel.is_deleted == False
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def find_by_laboratory(self, laboratory_id: LaboratoryId) -> List[Procedure]:
        stmt = (
            select(ProcedureModel)
            .join(LaboratoryProcedureModel, ProcedureModel.procedure_id == LaboratoryProcedureModel.procedure_id)
            .where(
                LaboratoryProcedureModel.laboratory_id == laboratory_id.value.bytes,
                ProcedureModel.is_deleted == False
            )
            .order_by(ProcedureModel.name)
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [ProcedureMapper.to_domain(model) for model in models]