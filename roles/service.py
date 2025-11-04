from abc import ABC, abstractmethod
from typing import Any, Type
from sqlalchemy.ext.asyncio import AsyncSession

from roles.repository import RolesRepository, RolesRepositoryPolicy
from roles.schemas import  OKResponce, Role
from roles.models import AvailableRoles



class RolesServicePolicy(ABC): 

  def __init__(self, repo: Type[RolesRepositoryPolicy]) -> None:
    self.repo = repo
    self.schema = Role


  @abstractmethod
  async def get_role(self, session: AsyncSession, role: AvailableRoles) -> OKResponce | None:
    pass


  @abstractmethod
  async def get_roles(self, session: AsyncSession) -> list[Role] | None:
    pass


  @abstractmethod
  async def insert_default_roles(self, session: AsyncSession) -> None:
    pass


  @abstractmethod
  async def is_role_exists(cls, session: AsyncSession, **filters: Any) -> bool:
    pass


  @abstractmethod
  def model_validate(self, data: Any) -> Role:
    pass


class _RolesService(RolesServicePolicy):

  async def get_role(self, session: AsyncSession, role: AvailableRoles) -> Role | None:
    result = await self.repo.get_role(session, role=role)

    if result is None:
      return None

    return self.model_validate(result)


  async def get_roles(self, session: AsyncSession) -> list[Role] | None:
    roles = await self.repo.get_roles(session)

    if not roles :
      return None

    return [self.model_validate(role) for role in roles]


  async def is_role_exists(self, session: AsyncSession, **filters: Any) -> bool:
    result = self.repo.get_role(session, **filters)

    if not result:
      return False

    return True


  async def insert_default_roles(self, session: AsyncSession) -> None:
    await self.repo.insert_default_roles(session)


  def model_validate(self, data: Any) -> Role:
    return self.schema.model_validate(data, from_attributes=True)


RolesService = _RolesService(RolesRepository)