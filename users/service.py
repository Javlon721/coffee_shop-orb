
from abc import ABC, abstractmethod
from typing import Any, Type

from sqlalchemy.ext.asyncio import AsyncSession

from auth.utils import hash_password
from db.config import DBConfig
from users.schemas import OKResponce, RegisterUser, UpdateUser, User
from users.repository import UsersRepository, UsersRepositoryPolicy


class UsersServicePolicy(ABC):


  def __init__(self, repo: Type[UsersRepositoryPolicy]) -> None:
    self.repo = repo
    self.schema =  User


  @abstractmethod
  async def get_user(self, session: AsyncSession, **filters: Any) -> User | None:
    """
      :params **kwargs: any (keyword, value) that matches users table columns
      >>> UsersServicePolicy.get_user(session, email="some@emil.com", is_verified=True, ...)
    """
    pass


  @abstractmethod
  async def create_user(self, session: AsyncSession, data: RegisterUser) -> OKResponce | None:
    pass


  @abstractmethod
  async def get_users(self, session: AsyncSession) -> list[User] | None:
    pass


  @abstractmethod
  async def delete_user(self, session: AsyncSession, user_id: int) -> OKResponce| None:
    pass


  @abstractmethod
  async def update_user(self, session: AsyncSession, user_id: int, update_info: UpdateUser) -> OKResponce | None:
    pass


  @abstractmethod
  async def verify_user(self, session: AsyncSession, user_id: int) -> OKResponce | None:
    pass


  @abstractmethod
  async def is_user_exist(self, session: AsyncSession, **filters: Any) -> bool:
    pass


  @classmethod
  @abstractmethod
  def model_validate(cls, data: Any) -> User:
    pass


class _UsersService(UsersServicePolicy):

  async def get_user(self, session: AsyncSession, **filters: Any) -> User | None:
    user = await self.repo.get_user(session, **filters)

    if not user:
      return None

    return self.model_validate(user)


  async def create_user(self, session: AsyncSession, data: RegisterUser) -> OKResponce | None:
    if await self.is_user_exist(session, email=data.email):
      return None

    hashed_password = hash_password(data.password)
    data.set_hashed_password(hashed_password)

    user_id = await self.repo.create_user(session, **data.model_dump(exclude_none=True, exclude_defaults=True))
    
    if user_id is None:
      return None

    return OKResponce(ok=True, user_id=user_id)


  async def get_users(self, session: AsyncSession) -> list[User] | None:
    users = await self.repo.get_users(session)
    
    if not users:
      return None
    
    return [self.model_validate(user) for user in users]


  async def delete_user(self, session: AsyncSession, user_id: int) -> OKResponce | None:
    if not await self.is_user_exist(session, user_id=user_id):
      return None

    deleted_user_id = await self.repo.delete_user(session, user_id)

    if deleted_user_id is None:
      return None

    return OKResponce(ok=True, user_id=deleted_user_id)


  async def update_user(self, session: AsyncSession, user_id: int, update_info: UpdateUser) -> OKResponce | None:
    user = await self.get_user(session, user_id=user_id)

    if user is None:
      return None

    if user.email:
      if user.email == update_info.email or await self.is_user_exist(session, email=user.email):
        return None

    result = await self.repo.update_user(session, user_id, **update_info.model_dump(exclude_none=True, exclude_defaults=True))

    if result is None:
      return None

    return OKResponce(ok=True, user_id=result)


  async def verify_user(self, session: AsyncSession, user_id: int) -> OKResponce | None:
    user = await self.get_user(session, user_id=user_id)

    if not user:
      return None

    if user.is_verified:
      return None

    result = await self.repo.update_user(session, user_id, is_verified=True)

    if result is None:
      return None

    return OKResponce(ok=True, user_id=result)


  async def is_user_exist(self, session: AsyncSession, **filters) -> bool:
    user = await self.get_user(session, **filters)

    if user is None:
      return False

    return True


  def model_validate(self, data: Any) -> User:
    return self.schema.model_validate(data, from_attributes=True)


  async def add_main_admin(self, session: AsyncSession) -> OKResponce | None:
    admin = RegisterUser(email=DBConfig.ADMIN_EMAIL, password=DBConfig.ADMIN_PASSWORD)

    result = await self.create_user(session, admin)

    assert result is not None

    await self.verify_user(session, result.user_id)

    await session.commit()

    return result


UsersService = _UsersService(UsersRepository)