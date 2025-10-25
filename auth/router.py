from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.config import AuthConfig
from auth.dependencies import renew_access_token
from auth.models import AccessToken, Tokens
from auth.utils import create_access_token, create_refresh_token, generate_verification_link, verify_password
from auth.verification.models import VerificationToken
from auth.verification.repository import VerificationRepository
from db.connection import AsyncSessionDepends
from users.models import RegisterUser, OKResponce, User, UserLogin
from users.repository import  UsersRepositoryNew
from users_roles.repository import UsersRolesRepositoryNew
from utils.utils import pretty_print


auth_router = APIRouter(prefix="/auth", tags=["auth"])


async def authenticate_user(session: AsyncSession, user: UserLogin) -> User | None:
  user_credential = await UsersRepositoryNew.get_user(session, email=user.email)
  
  if not user_credential:
    return None
  
  if not verify_password(user.password, user_credential.password):
    return None

  return user_credential


async def get_user_roles(session: AsyncSession, user_id: int) -> str:
  roles = await UsersRolesRepositoryNew.get_roles_by(session, user_id)
  
  if not roles:
    return ""
  
  return " ".join([role.role for role in roles])


async def send_verification_link(session: AsyncSession, user_id: int, req: Request):
  v_token = await VerificationRepository.add(session, user_id)

  if v_token is None:
    raise HTTPException(detail=f"some errors occured", status_code=status.HTTP_400_BAD_REQUEST)

  base_url = str(req.base_url).rstrip('/')
  verification_link = generate_verification_link(base_url, v_token.token)

  pretty_print("VERIFICATION LINK ->", verification_link, sep_cnt=30)

  return verification_link


@auth_router.post("/signup")
async def signup_new(user: RegisterUser, background_tasks: BackgroundTasks, req: Request, session: AsyncSessionDepends):
  result = await UsersRepositoryNew.create_user(session, user)

  if result is None:
    raise HTTPException(detail=f"user {user.email} already exists", status_code=status.HTTP_400_BAD_REQUEST)

  background_tasks.add_task(send_verification_link, session, result.user_id, req)

  return result


@auth_router.post(f"/{AuthConfig.VERIFICATION_ENDPOINT_PATH}")
async def verify(token: VerificationToken, session: AsyncSessionDepends) -> OKResponce:
  verification = await VerificationRepository.get(session, token.token)

  if verification is None:
    raise HTTPException(detail=f"token invalid or expired", status_code=status.HTTP_400_BAD_REQUEST)

  result = await UsersRepositoryNew.verify_user(session, verification.user_id)

  if result is None:
    raise HTTPException(detail=f"user already verified", status_code=status.HTTP_400_BAD_REQUEST)

  return result


@auth_router.post("/login")
async def login(user: UserLogin, session: AsyncSessionDepends) -> Tokens:
  user_credentials = await authenticate_user(session, user)
  
  if not user_credentials:
    raise HTTPException(detail=f"invalid user credentials", status_code=status.HTTP_403_FORBIDDEN)

  user_roles = await get_user_roles(session, user_credentials.user_id)

  data = {"user_id": user_credentials.user_id, "roles": user_roles}
  
  access_token = create_access_token(data)
  refresh_token = create_refresh_token(data)

  return Tokens(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


@auth_router.post("/refresh")
async def refresh(new_access_token: Annotated[AccessToken, Depends(renew_access_token)]):
  return new_access_token
