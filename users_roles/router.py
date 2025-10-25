
from fastapi import APIRouter, HTTPException, status

from auth.dependencies import AdminDependency
from db.connection import AsyncSessionDepends
from roles.models import UserRole
from users_roles.models import RegisterUserRole, OKResponce, UserRoles
from users_roles.repository import UsersRolesRepository


users_roles_router = APIRouter(prefix="/usersroles", tags=["users_roles"])


@users_roles_router.get('/', dependencies=[AdminDependency])
async def get_all(session: AsyncSessionDepends) -> list[UserRoles]:
  result = await UsersRolesRepository.get_all(session)
  
  if result is None:
    raise HTTPException(detail=f"users_roles not found", status_code=status.HTTP_404_NOT_FOUND)
  
  return result


@users_roles_router.get('/{user_id}', dependencies=[AdminDependency])
async def get_user_roles(user_id: int, session: AsyncSessionDepends) -> list[UserRole]:
  result = await UsersRolesRepository.get_roles_by(session, user_id)

  if result is None:
    raise HTTPException(detail=f"user roles not found", status_code=status.HTTP_404_NOT_FOUND)

  return result


@users_roles_router.post('/', dependencies=[AdminDependency])
async def add_role_to_user(data: RegisterUserRole, session: AsyncSessionDepends) -> OKResponce:
  return await UsersRolesRepository.add(session, data)
