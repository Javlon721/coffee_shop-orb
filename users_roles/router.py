

from fastapi import APIRouter, HTTPException, status

from auth.dependencies import AdminDependency
from roles.models import UserRole
from users_roles.models import RegisterUserRole, OKResponce, UserRoles
from users_roles.repository import UsersRolesRepository


users_roles_router = APIRouter(prefix="/usersroles", tags=["users_roles"])


@users_roles_router.get('/', dependencies=[AdminDependency])
def get_all() -> list[UserRoles]:
  result = UsersRolesRepository.get_all()
  
  if result is None:
    raise HTTPException(detail=f"users_roles not found", status_code=status.HTTP_404_NOT_FOUND)
  
  return result


@users_roles_router.get('/{user_id}', dependencies=[AdminDependency])
def get_user_roles(user_id: int) -> list[UserRole]:
  result = UsersRolesRepository.get_roles_by(user_id)

  if result is None:
    raise HTTPException(detail=f"user roles not found", status_code=status.HTTP_404_NOT_FOUND)

  return result


@users_roles_router.post('/', dependencies=[AdminDependency])
def add_role_to_user(data: RegisterUserRole) -> OKResponce:
  return UsersRolesRepository.add(data)
