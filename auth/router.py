from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.config import AuthConfig
from auth.dependencies import renew_access_token
from auth.models import AccessToken, Tokens
from auth.utils import create_access_token, create_refresh_token, generate_verification_link, verify_password
from auth.verification.schemas import VerificationToken
from auth.verification.service import VerificationService
from db.connection import AsyncSessionDepends
from users.schemas import RegisterUser, OKResponce, User, UserLogin
from users.service import UsersService
from users_roles.repository import UsersRolesRepository
from utils.utils import pretty_print


auth_router = APIRouter(prefix="/auth", tags=["auth"])


async def authenticate_user(session: AsyncSession, user: UserLogin) -> User | None:
  user_credential = await UsersService.get_user(session, email=user.email)
  
  if not user_credential:
    return None
  
  if not verify_password(user.password, user_credential.password):
    return None

  return user_credential


async def get_user_roles(session: AsyncSession, user_id: int) -> str:
  """
  Gets user roles from DB by *user_id*

  :returns: string that joined with space (i.e. "user admin superadmin")
  
  """  
  roles = await UsersRolesRepository.get_roles_by(session, user_id)
  
  if not roles:
    return ""
  
  return " ".join([role.role for role in roles])


async def send_verification_link(session: AsyncSession, user_id: int, req: Request):
  """
  For simplicity i make verification url printed to the console
  
  Ideally it should send a html generated responce
  """  
  v_token = await VerificationService.add_token(session, user_id)

  if v_token is None:
    raise HTTPException(detail=f"some errors occured", status_code=status.HTTP_400_BAD_REQUEST)

  base_url = str(req.base_url).rstrip('/')
  verification_link = generate_verification_link(base_url, v_token.token)

  pretty_print("VERIFICATION LINK ->", verification_link, sep_cnt=30)

  return verification_link


@auth_router.post("/signup", 
  summary="Create an new user",
  responses={
    "400": {
      "description": "User exists error",
      "content": {
        "application/json": {
            "example": {"detail": "user some@mail.ru already exists"}
          }
      }
    },
    "200":{
      "model": OKResponce,
      "description": "Returns new created user",
            "content": {
                "application/json": {
                    "example": {"ok": True, "user_id": 1}
                }
            },
    }
  },
)
async def signup(
  user: RegisterUser, 
  background_tasks: BackgroundTasks, 
  req: Request, 
  session: AsyncSessionDepends
) -> OKResponce:
  """
    Create a new user:
    
    - **email**: string
    - **password**: string
    - **first_name**: string | None
    - **last_name**: string | None
  """
  
  result = await UsersService.create_user(session, user)

  if result is None:
    raise HTTPException(detail=f"user {user.email} already exists", status_code=status.HTTP_400_BAD_REQUEST)

  # TODO: session may be closed
  # background_tasks.add_task(send_verification_link, session, result.user_id, req)
  # background_tasks.add_task(UsersRolesRepository.add_default_user_role, session, result.user_id)

  await session.commit()

  return result


@auth_router.post(f"/{AuthConfig.VERIFICATION_ENDPOINT_PATH}",
  responses={
    "200":{
      "model": OKResponce,
      "description": "Returns verified user_id",
      "content": {
          "application/json": {
              "example": {"ok": True, "user_id": 1}
          }
      },
    },
    "400": {
      "description": "User already verified error",
      "content": {
        "application/json": {
            "example": {"detail": "user already verified"}
          }
      }
    },
    "403": {
      "description": "Token invalid or expired error",
      "content": {
        "application/json": {
            "example": {"detail": "token invalid or expired"}
          }
      }
    },
  },
)
async def verify(token: VerificationToken, session: AsyncSessionDepends) -> OKResponce:
  """
    Verifies user by given verification token
    
    - **token**: string
  """
  verification = await VerificationService.get_valid_token(session, token.token)

  if verification is None:
    raise HTTPException(detail=f"token invalid or expired", status_code=status.HTTP_403_FORBIDDEN)

  result = await UsersService.verify_user(session, verification.user_id)

  if result is None:
    raise HTTPException(detail=f"user already verified", status_code=status.HTTP_400_BAD_REQUEST)

  return result


@auth_router.post("/login",
  responses={
    "200":{
      "model": Tokens,
      "description": "Returns authenticated user tokes",
      "content": {
        "application/json": {
            "example": {"access_token": "string", "refresh_token": "string", "token_type": "bearer"}
        }
      },
    },
    "401": {
      "description": "Invalid user credentials error",
      "content": {
        "application/json": {
            "example": {"detail": "invalid user credentials"}
          }
      }
    },
  }
)
async def login(user: UserLogin, session: AsyncSessionDepends) -> Tokens:
  """
    Loging in user by
    
    - **email**: string
    - **password**: string
  """
  user_credentials = await authenticate_user(session, user)
  
  if not user_credentials:
    raise HTTPException(detail=f"invalid user credentials", status_code=status.HTTP_401_UNAUTHORIZED)

  user_roles = await get_user_roles(session, user_credentials.user_id)

  data = {"user_id": user_credentials.user_id, "roles": user_roles}
  
  access_token = create_access_token(data)
  refresh_token = create_refresh_token(data)

  return Tokens(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


@auth_router.post("/refresh",
  responses={
    "200":{
      "model": AccessToken,
      "description": "Returns new access token",
      "content": {
        "application/json": {
          "example": {"access_token": "string", "token_type": "bearer"}
        }
      },
    },
    "400": {
      "description": "Access token expired error",
      "content": {
        "application/json": {
          "example": {"detail": "Access token expired"}
        }
      }
    },
    "401": {
      "description": "Invalid user credentials error",
      "content": {
        "application/json": {
          "example": {"detail": "Could not validate credentials"}
        }
      }
    },
  },
  openapi_extra={
    "parameters": [
      {
        "name": "Authorization",
        "in": "header",
        "required": True,
        "schema": {"type": "string"},
        "description": "String with refresh_token bearer",
        "example": "Bearer refresh_token_here"
      }
    ]
  }
)
async def refresh(new_access_token: Annotated[AccessToken, Depends(renew_access_token)]):
  return new_access_token
