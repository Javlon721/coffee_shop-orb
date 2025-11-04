from abc import ABC, abstractmethod
from typing import Any, Type

from sqlalchemy.ext.asyncio import AsyncSession

from roles.models import AvailableRoles
from roles.schemas import UserRole
from roles.service import RolesService, RolesServicePolicy
from users.service import UsersService, UsersServicePolicy
from users_roles.repository import UsersRolesRepositoryNew, UsersRolesRepositoryPolicy
from users_roles.schemas import RegisterUserRole, UserRoles



class UsersRolesServicePolicy(ABC):

  def __init__(
    self, 
    repo: Type[UsersRolesRepositoryPolicy], 
    users_service: UsersServicePolicy, 
    roles_service: RolesServicePolicy
  ) -> None:
    self.repo = repo
    self.schema = UserRoles
    self.users_service = users_service
    self.roles_service = roles_service


  @abstractmethod
  async def get_roles_by(self, session: AsyncSession, user_id: int) -> list[UserRoles] | None:
    pass


  @abstractmethod
  async def get_all(self, session: AsyncSession) -> list[UserRoles] | None:
    pass


  @abstractmethod
  async def add(self, session: AsyncSession, data: RegisterUserRole) -> int | None:
    pass


  @abstractmethod
  async def add_default_user_role(self, session: AsyncSession, user_id: int) -> int | None:
    pass


  @abstractmethod
  async def add_main_admin_roles(self, session: AsyncSession, user_id: int) -> int | None:
    pass


  def model_validate(self, data: Any) -> UserRoles:
    return self.schema.model_validate(data, from_attributes=True)


class _UsersRolesService(UsersRolesServicePolicy):

  async def get_roles_by(self, session: AsyncSession, user_id: int) -> list[UserRole] | None:
    roles = await self.repo.get_roles_by(session, user_id)

    if not roles:
      return None

    return [UserRole.model_validate(role, from_attributes=True) for role in roles]


  async def get_all(self, session: AsyncSession) -> list[UserRoles] | None:
    roles = await self.repo.get_all_by(session)

    if not roles:
      return None

    return [self.model_validate(role) for role in roles]


  async def add(self, session: AsyncSession, data: RegisterUserRole) -> int | None:
    if not await self.users_service.is_user_exist(session, user_id=data.user_id):
      return None

    if not await self.roles_service.is_role_exists(session, role_id=data.role_id):
      return None

    new_user_roles = data.model_dump()

    user_roles = await self.repo.get_all_by(session, **new_user_roles)

    for role in user_roles:
      if data.role_id == role.role_id:
        return None

    result = await self.repo.add(session, **new_user_roles)

    return result


  async def add_default_user_role(self, session: AsyncSession, user_id: int) -> int | None:
    default_user_role = AvailableRoles.USER

    return await self.add_role_by(session, user_id, default_user_role)


  async def add_main_admin_roles(self, session: AsyncSession, user_id: int) -> int | None:
    default_user_role = AvailableRoles.ADMIN

    return await self.add_role_by(session, user_id, default_user_role)


  async def add_role_by(self, session: AsyncSession, user_id: int, role: AvailableRoles) -> int | None:
    if not await self.users_service.is_user_exist(session, user_id=user_id):
      return None

    resp = await self.roles_service.get_role(session, role)

    if not resp:
      return None

    new_user_role = RegisterUserRole(user_id=user_id, role_id=resp.role_id)

    user_roles = await self.repo.get_all_by(session, **new_user_role.model_dump())

    for item in user_roles:
      if new_user_role.role_id == item.role_id:
        return None

    result = await self.repo.add(session, **new_user_role.model_dump())

    return result


UsersRolesService = _UsersRolesService(UsersRolesRepositoryNew, UsersService, RolesService)