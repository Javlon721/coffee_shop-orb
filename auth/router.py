from typing import Annotated
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status

from auth.dependencies import renew_access_token
from auth.models import AccessToken, Tokens
from auth.utils import create_access_token, create_refresh_token, generate_verification_link, verify_password
from auth.verification.repository import VerificationRepository
from users.models import RegisterUser, OKResponce, User, UserLogin
from users.repository import UsersRepository, get_user_credentials
from users_roles.repository import UsersRolesRepository
from utils.utils import pretty_print


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


def send_verification_link(user_id: int, req: Request):
  token = VerificationRepository.add(user_id)

  if token is None:
    raise HTTPException(detail=f"some errors occured", status_code=status.HTTP_400_BAD_REQUEST)

  base_url = str(req.base_url).rstrip('/')
  verification_link = generate_verification_link(base_url, token)

  pretty_print("VERIFICATION LINK ->", verification_link, sep_cnt=30)

  return verification_link


@auth_router.post("/signup")
def signup(user: RegisterUser, background_tasks: BackgroundTasks, req: Request) -> OKResponce:
  result = UsersRepository.create(user)

  background_tasks.add_task(send_verification_link, result.user_id, req)

  return result


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
