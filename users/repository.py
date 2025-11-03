from abc import ABC, abstractmethod
from typing import Any, Sequence

from sqlalchemy import delete, insert, text, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from users.models import UsersORM



class UsersRepositoryPolicy(ABC):

  model = UsersORM


  @classmethod
  @abstractmethod
  async def create_user(cls, session: AsyncSession, **data: Any) -> int | None:
    pass


  @classmethod
  @abstractmethod
  async def get_user(cls, session: AsyncSession, **filters: Any) -> UsersORM | None:
    """
      :params **filters: any (keyword, value) that matches users table columns
      >>> UsersRepositoryPolicy.get_user(session, email="some@emil.com", is_verified=True, ...)
    """
    pass


  @classmethod
  @abstractmethod
  async def get_users(cls, session: AsyncSession) -> Sequence[UsersORM]:
    pass


  @classmethod
  @abstractmethod
  async def delete_user(cls, session: AsyncSession, user_id: int) -> None:
    pass


  @classmethod
  @abstractmethod
  async def delete_users(cls, session: AsyncSession, users_id: list[int])-> Sequence[int]:
    pass


  @classmethod
  @abstractmethod
  async def update_user(cls, session: AsyncSession, user_id: int, **data: Any) -> int | None:
    pass


class UsersRepository(UsersRepositoryPolicy):
  @classmethod
  async def create_user(cls, session: AsyncSession, **data: Any) -> int | None:
    """
    :returns int | None: return new created `user_id` or None otherwise
    """    
    stmt = insert(cls.model).values(**data).returning(UsersORM.user_id)

    result = await session.execute(stmt)

    return result.scalar_one_or_none()


  @classmethod
  async def get_user(cls, session: AsyncSession, **filters: Any) -> UsersORM | None:
    query = select(cls.model).filter_by(**filters)

    result = await session.execute(query)

    return result.scalar_one_or_none()


  @classmethod
  async def get_users(cls, session: AsyncSession) -> Sequence[UsersORM]:
    query = select(cls.model)

    result = await session.execute(query)

    return result.scalars().all()


  @classmethod
  async def delete_user(cls, session: AsyncSession, user_id: int) -> int | None:
    """
    :returns int | None: return deleted `user_id` or None otherwise
    """    
    stmt = delete(cls.model).filter_by(user_id=user_id).returning(cls.model.user_id)

    result = await session.execute(stmt)

    return result.scalar_one_or_none()


  @classmethod
  async def delete_users(cls, session: AsyncSession, users_id: list[int])-> Sequence[int]:
    stmt = delete(cls.model).filter(cls.model.user_id.in_(users_id)).returning(UsersORM.user_id)

    result = await session.execute(stmt)

    return result.scalars().all()


  @classmethod
  async def update_user(cls, session: AsyncSession, user_id: int, **data: Any) -> int | None:
    """
    :returns int | None: return updated `user_id` or None otherwise
    """    
    stmt = update(cls.model).values(**data).filter_by(user_id=user_id).returning(cls.model.user_id)
    
    result = await session.execute(stmt)
    
    return result.scalar_one_or_none()


  @classmethod
  async def truncate_table(cls, session: AsyncSession):
    await session.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE"))
    await session.commit()