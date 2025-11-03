from abc import ABC, abstractmethod
from typing import Any, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from roles.models import AvailableRoles, RolesORM



class RolesRepositoryPolicy(ABC):

  model = RolesORM


  @classmethod
  @abstractmethod
  async def get_role(cls, session: AsyncSession, **filters: Any) -> RolesORM | None:
    pass


  @classmethod
  @abstractmethod
  async def get_roles(cls, session: AsyncSession) -> list[RolesORM]:
    pass


  @classmethod
  @abstractmethod
  async def insert_default_roles(cls, session: AsyncSession) -> None:
    pass



class RolesRepository(RolesRepositoryPolicy):

  @classmethod
  async def get_role(cls, session: AsyncSession, **filters: Any) -> RolesORM | None:
    query = select(cls.model).filter_by(**filters)
    
    result = await session.execute(query)
    
    return result.scalar_one_or_none()


  @classmethod
  async def get_roles(cls, session: AsyncSession) -> Sequence[RolesORM]:
    query = select(cls.model)

    result = await session.execute(query)

    return result.scalars().all()


  @classmethod
  async def insert_default_roles(cls, session: AsyncSession) -> None:
    roles = [RolesORM(role=role) for role in AvailableRoles]

    session.add_all(roles)

    await session.commit()