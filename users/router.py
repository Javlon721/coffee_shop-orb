

from fastapi import APIRouter

from users.models import OKResponce, User
from users.repository import UsersRepository


users_router = APIRouter(prefix="/users", tags=["users"])


@users_router.get('/{user_id}')
def get_user(user_id: int) -> User:
  return UsersRepository.get_user(user_id)


@users_router.delete('/{user_id}')
def delete_user(user_id: int) -> OKResponce:
  return UsersRepository.delete_user(user_id)