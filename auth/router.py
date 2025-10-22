from fastapi import APIRouter

from users.models import RegisterUser, OKResponce
from users.repository import UsersRepository


auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/signup")
def signup(user: RegisterUser) -> OKResponce:
  return UsersRepository.create(user)