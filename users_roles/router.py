

from fastapi import APIRouter

from roles.models import UserRole
from users_roles.models import RegisterUserRole, OKResponce, UserRoles
from users_roles.repository import UsersRolesRepository


users_roles_router = APIRouter(prefix="/usersroles", tags=["users_roles"])


@users_roles_router.get('/')
def get_all() -> list[UserRoles]:
  return UsersRolesRepository.get_all()


@users_roles_router.get('/{user_id}')
def get_user_rolles(user_id: int) -> list[UserRole]:
  return UsersRolesRepository.get_roles_by(user_id)


@users_roles_router.post('/')
def add_role_to_user(data: RegisterUserRole) -> OKResponce:
  return UsersRolesRepository.add(data)
