from typing import Annotated
from fastapi import APIRouter, HTTPException, status

from auth.dependencies import AdminDependency, ValidUserDependency, is_admin
from db.connection import AsyncSessionDepends
from users.models import OKResponce, UpdateUser, User, UserWithRoles
from users.repository import UsersRepository, UsersRepositoryNew


users_router = APIRouter(prefix="/users", tags=["users"])
users_router_new = APIRouter(prefix="/v2/users", tags=["users"])


@users_router.get('/me')
def get_me(user: Annotated[UserWithRoles, ValidUserDependency]) -> User:
  return user.user


@users_router.get('/{user_id}', dependencies=[AdminDependency])
def get_user(user_id: int) -> User:
  user = UsersRepository.get_user(user_id)

  if user is None:
    raise HTTPException(detail=f"user {user_id} does not exists", status_code=status.HTTP_404_NOT_FOUND)

  return user


@users_router_new.get('/{user_id}', dependencies=[])
async def get_user_new(user_id: int,  session: AsyncSessionDepends) -> User:
  user = await UsersRepositoryNew.get_user(session, user_id)

  if user is None:
    raise HTTPException(detail=f"user {user_id} does not exists", status_code=status.HTTP_404_NOT_FOUND)

  return user


@users_router.delete('/{user_id}', dependencies=[AdminDependency])
def delete_user(user_id: int) -> OKResponce:
  result = UsersRepository.delete_user(user_id)

  if result is None:
    raise HTTPException(detail=f"user {user_id} does not exists", status_code=status.HTTP_400_BAD_REQUEST)

  return result


@users_router.get('/', dependencies=[AdminDependency])
def get_all_users() -> list[User]:
  result = UsersRepository.get_all_users()

  if result is None:
    raise HTTPException(detail=f"users not found", status_code=status.HTTP_404_NOT_FOUND)

  return result


@users_router_new.get('/', dependencies=[])
async def get_all_users_new(session: AsyncSessionDepends) -> list[User]:
  result = await UsersRepositoryNew.get_users(session)

  if result is None:
    raise HTTPException(detail=f"users not found", status_code=status.HTTP_404_NOT_FOUND)

  return result


@users_router.patch('/{user_id}')
def update_user(user_id: int, user: UpdateUser, current_user: Annotated[UserWithRoles, ValidUserDependency]) -> OKResponce:
  if not is_admin(current_user):
    if current_user.user.user_id != user_id:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
      )
  
  if not user.model_dump(exclude_none=True, exclude_defaults=True):
    raise HTTPException(detail=f"update info not provided", status_code=status.HTTP_400_BAD_REQUEST)

  return UsersRepository.update_user(user_id, user)