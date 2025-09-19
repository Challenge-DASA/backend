from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.material import Material
from domain.repositories.material import MaterialRepository
from domain.value_objects.ids import MaterialId
from infrastructure.storage.mappers.material import MaterialMapper
from infrastructure.storage.models.material import MaterialModel


class MaterialRepositoryImpl(MaterialRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_id(self, material_id: MaterialId) -> Optional[Material]:
        stmt = select(MaterialModel).where(
            MaterialModel.material_id == material_id.value.bytes,
            MaterialModel.is_deleted == False
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return MaterialMapper.to_domain(model)

    async def find_by_multiple_ids(self, material_ids: List[MaterialId]) -> List[Material]:
        if not material_ids:
            return []

        material_bytes = [mid.value.bytes for mid in material_ids]

        stmt = select(MaterialModel).where(
            MaterialModel.material_id.in_(material_bytes),
            MaterialModel.is_deleted == False
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [MaterialMapper.to_domain(model) for model in models]

    async def exists(self, material_id: MaterialId) -> bool:
        stmt = select(MaterialModel).where(
            MaterialModel.material_id == material_id.value.bytes,
            MaterialModel.is_deleted == False
        )
        result = await self.session.execute(stmt)
        return result.scalar() is not None