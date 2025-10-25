from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from roles.models import AvailableRoles, Role, RolesORM


class RolesRepository:

  @staticmethod
  async def get_roles(session: AsyncSession) -> list[Role] | None:
    query = select(RolesORM)

    res = await session.scalars(query)
    result = res.all()
    
    if not result:
      return None

    return [Role.model_validate(role, from_attributes=True) for role in result]


  @staticmethod
  async def insert_default_roles(session: AsyncSession) -> None:
    session.add_all([RolesORM(role=role) for role in AvailableRoles])
    await session.commit()