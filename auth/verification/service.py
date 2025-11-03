
from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any, Type, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from auth.config import AuthConfig
from auth.utils import generate_verification_token, get_expiration_time
from auth.verification.repository import VerificationRepository, VerificationRepositoryPolicy
from auth.verification.schemas import Verification, VerificationToken


class VerificationServicePolicy(ABC):
  
  def __init__(self, repo: Type[VerificationRepositoryPolicy]) -> None:
    self.repo = repo
    self.schema = Verification


  @abstractmethod
  async def add_token(cls, session: AsyncSession, user_id: int) -> VerificationToken:
    pass


  @abstractmethod
  async def get_valid_token(cls, session: AsyncSession, token: str) -> Verification | None:
    pass


  @abstractmethod
  async def get_expired_users_id(cls, session: AsyncSession) -> Sequence[int]:
    pass


  @abstractmethod
  async def truncate_table(cls, session: AsyncSession) -> None:
    pass
  
  @abstractmethod
  def model_validate(self, data: Any) -> Verification:
    pass


class _VerificationService(VerificationServicePolicy):

  async def add_token(self, session: AsyncSession, user_id: int) -> Verification:
    default_time_delta = timedelta(days=AuthConfig.VERIFICATION_TOKEN_EXPIRE_DAYS)

    expires_at = get_expiration_time(default_time_delta)
    token = generate_verification_token()

    result = await self.repo.add_token(session, user_id=user_id, expires_at=expires_at, token=token)

    return self.model_validate(result)


  async def get_valid_token(self, session: AsyncSession, token: str) -> Verification | None:
    result = await self.repo.get_valid_token(session, token=token)
    
    return  self.model_validate(result)


  async def get_expired_users_id(self, session: AsyncSession) -> Sequence[int]:
    result = await self.repo.get_expired_users_id(session)
    
    return result


  async def truncate_table(self, session: AsyncSession) -> None:
    await self.repo.truncate_table(session)


  def model_validate(self, data: Any) -> Verification:
    return self.schema.model_validate(data, from_attributes=True)


VerificationService = _VerificationService(VerificationRepository)