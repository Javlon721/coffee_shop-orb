from abc import ABC, abstractmethod
from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select
from sqlalchemy.orm import aliased

from src.roles.models import RolesORM
from src.users_roles.models import UsersRolesORM



class UsersRolesRepositoryPolicy(ABC):

  model = UsersRolesORM


  @classmethod
  @abstractmethod
  async def get_roles_by(cls, session: AsyncSession, user_id: int) -> Sequence[UsersRolesORM]:
    pass


  @classmethod
  @abstractmethod
  async def get_all_by(cls, session: AsyncSession, **filters: Any) -> Sequence[UsersRolesORM]:
    pass


  @classmethod
  @abstractmethod
  async def add(cls, session: AsyncSession, **data: Any) -> int | None:
    pass




class UsersRolesRepositoryNew(UsersRolesRepositoryPolicy):

  @classmethod
  async def get_roles_by(cls, session: AsyncSession, user_id: int) -> Sequence[str]:
    ur = aliased(cls.model)
    r = aliased(RolesORM)

    query = select(r.role).join(ur, r.role_id == ur.role_id).filter_by(user_id=user_id)

    result = await session.execute(query)

    return result.scalars().all()


  @classmethod
  async def get_all_by(cls, session: AsyncSession, **filters: Any) -> Sequence[UsersRolesORM]:
    query = select(cls.model).filter_by(**filters)

    result = await session.execute(query)

    return result.scalars().all()


  @classmethod
  async def add(cls, session: AsyncSession, **data: Any) -> int | None:
    stmt = insert(cls.model).values(**data).returning(cls.model.id)

    result = await session.execute(stmt)

    return result.scalar_one_or_none()