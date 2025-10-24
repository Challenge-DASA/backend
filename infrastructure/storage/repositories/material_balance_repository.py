from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.material_balance import MaterialBalance
from domain.repositories.material import MaterialBalanceRepository
from domain.value_objects.ids import MaterialId, LaboratoryId
from infrastructure.storage.mappers.material_balance import MaterialBalanceMapper
from infrastructure.storage.models.material_balance import MaterialBalanceModel


class MaterialBalanceRepositoryImpl(MaterialBalanceRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, balance: MaterialBalance) -> None:
        balance_model = MaterialBalanceMapper.to_model(balance)

        await self.session.merge(balance_model)
        await self.session.commit()

    async def find_by_material_and_laboratory(
            self,
            material_id: MaterialId,
            laboratory_id: LaboratoryId
    ) -> Optional[MaterialBalance]:
        stmt = select(MaterialBalanceModel).where(
            MaterialBalanceModel.material_id == material_id.value,
            MaterialBalanceModel.laboratory_id == laboratory_id.value
        )

        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        return MaterialBalanceMapper.to_domain(model) if model else None

    async def find_by_laboratory(self, laboratory_id: LaboratoryId) -> List[MaterialBalance]:
        stmt = select(MaterialBalanceModel).where(
            MaterialBalanceModel.laboratory_id == laboratory_id.value
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [MaterialBalanceMapper.to_domain(model) for model in models]

    async def find_multiple_by_laboratory(
            self,
            material_ids: List[MaterialId],
            laboratory_id: LaboratoryId
    ) -> List[MaterialBalance]:
        material_uuids = [mid.value for mid in material_ids]

        stmt = select(MaterialBalanceModel).where(
            MaterialBalanceModel.material_id.in_(material_uuids),
            MaterialBalanceModel.laboratory_id == laboratory_id.value
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [MaterialBalanceMapper.to_domain(model) for model in models]