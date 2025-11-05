from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any, Sequence

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from src.auth.utils import  get_utc_time
from src.auth.verification.models import VerificationsORM



class VerificationRepositoryPolicy(ABC):

  model = VerificationsORM


  @classmethod
  @abstractmethod
  async def add_token(cls, session: AsyncSession, **data: Any) -> VerificationsORM:
    pass


  @classmethod
  @abstractmethod
  async def get_valid_token(cls, session: AsyncSession, **filters: Any) -> VerificationsORM | None:
    pass


  @classmethod
  @abstractmethod
  async def get_expired_users_id(cls, session: AsyncSession, **filters: Any) -> Sequence[int]:
    pass


  @classmethod
  @abstractmethod
  async def truncate_table(cls, session: AsyncSession) -> None:
    pass


class VerificationRepository(VerificationRepositoryPolicy):

  @classmethod
  async def add_token(cls, session: AsyncSession, **data: Any) -> VerificationsORM:
    stmt = insert(cls.model).values(**data).returning(cls.model)

    result = await session.execute(stmt)

    return result.scalar_one()


  @classmethod
  async def get_valid_token(cls, session: AsyncSession, **filters: Any) -> VerificationsORM | None:
    now = get_utc_time()

    query = select(cls.model).filter_by(**filters).filter(cls.model.expires_at >= now)

    result = await session.execute(query)

    return result.scalar_one_or_none()


  @classmethod
  async def get_expired_users_id(cls, session: AsyncSession, expire_delta: timedelta = timedelta()) -> Sequence[int]:
    now = get_utc_time() + expire_delta

    query = select(cls.model.user_id).filter(now >= cls.model.expires_at)

    result = await session.execute(query)
    
    return result.scalars().all()


  @classmethod
  async def truncate_table(cls, session: AsyncSession) -> None:
    await session.execute(text("TRUNCATE TABLE verifications RESTART IDENTITY CASCADE"))
    await session.commit()