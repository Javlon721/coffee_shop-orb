from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Security, status

from auth.dependencies import renew_access_token, get_current_user
from auth.models import AccessToken, AccessTokenData, Tokens
from auth.utils import create_access_token, create_refresh_token, verify_password
from users.models import RegisterUser, OKResponce, User, UserLogin
from users.repository import UsersRepository, get_user_credentials
from users_roles.repository import UsersRolesRepository


auth_router = APIRouter(prefix="/auth", tags=["auth"])


def authenticate_user(user: UserLogin) -> User | None:
  user_credential = get_user_credentials(user.email)
  
  if not user_credential:
    return None
  
  if not verify_password(user.password, user_credential.password):
    return None

  return user_credential


def get_user_roles(user_id: int) -> str:
  roles = UsersRolesRepository.get_roles_by(user_id)
  
  if not roles:
    return ""
  
  return " ".join([role.role for role in roles])


@auth_router.post("/signup")
def signup(user: RegisterUser) -> OKResponce:
  return UsersRepository.create(user)


@auth_router.post("/login")
def login(user: UserLogin) -> Tokens:
  user_credentials = authenticate_user(user)
  
  if not user_credentials:
    raise HTTPException(detail=f"invalid user credentials", status_code=status.HTTP_403_FORBIDDEN)

  user_roles = get_user_roles(user_credentials.user_id)

  data = {"sub": str(user_credentials.user_id), "roles": user_roles}
  
  access_token = create_access_token(data)
  refresh_token = create_refresh_token(data)

  return Tokens(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


@auth_router.post("/refresh")
def refresh(new_access_token: Annotated[AccessToken, Depends(renew_access_token)]):
  return new_access_token
