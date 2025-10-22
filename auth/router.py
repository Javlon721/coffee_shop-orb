from typing import Annotated
from fastapi import APIRouter, HTTPException, status

from auth.dependencies import RenewAccessToken
from auth.models import AccessToken, Tokens
from auth.utils import create_access_token, create_refresh_token, verify_password
from users.models import RegisterUser, OKResponce, UserLogin
from users.repository import UsersRepository


auth_router = APIRouter(prefix="/auth", tags=["auth"])


def authenticate_user(user: UserLogin) -> UserLogin | None:
  user_credential = get_user_credentials(user.email)
  
  if not user_credential:
    return None
  
  if not verify_password(user.password, user_credential.password):
    return None

  return user_credential


def get_user_credentials(email: str) -> UserLogin | None:
  return UsersRepository.get_user_login_data(email)


@auth_router.post("/signup")
def signup(user: RegisterUser) -> OKResponce:
  return UsersRepository.create(user)


@auth_router.post("/login")
def login(user: UserLogin) -> Tokens:
  user_credentials = authenticate_user(user)
  
  if not user_credentials:
    raise HTTPException(detail=f"invalid user credentials", status_code=status.HTTP_403_FORBIDDEN)

  # todo: need to use user_id instead + add user_roles
  data = {"sub": user_credentials.email}
  
  access_token = create_access_token(data)
  refresh_token = create_refresh_token(data)

  return Tokens(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


@auth_router.post("/refresh")
def refresh(new_access_token: Annotated[AccessToken, RenewAccessToken]):
  return new_access_token
