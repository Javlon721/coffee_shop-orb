from typing import Annotated
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from auth.dependencies import AdminDependency, ValidUserDependency, is_admin
from db.connection import AsyncSessionDepends
from users.models import OKResponce, UpdateUser, User, UserWithRoles
from users.repository import UsersRepository


users_router = APIRouter(prefix="/users", tags=["users"])

authorization_header = {
  "parameters": [
    {
      "name": "Authorization",
      "in": "header",
      "required": True,
      "schema": {"type": "string"},
      "description": "String with access_token bearer",
      "example": "Bearer access_token_here"
    }
  ]
}

token_responses = {
  "400": {
    "description": "Refresh token expired error",
    "content": {
      "application/json": {
        "example": {"detail": "Refresh token expired"}
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
}

not_found_responce = {
  "404": {
    "description": "Not found error",
    "content": {
      "application/json": {
        "example": {"detail": "User email/user_id not found"}
      }
    }
  },
}


@users_router.get('/me', 
  openapi_extra={
    **authorization_header
  },
  responses={
    "200":{
      "model": User,
      "description": "Returns token holder user info",
      "content": {
        "application/json": {
          "example": {
            "email": "some1@mail.ru",
            "password": "$argon2id$v=19$m=65536,t=3,p=4$RILMC5LB/l/RkFPztO5YIQ$ePFKMnyP3YmMb0EfO4MvXgmj0ew4sm+3UcJEueUVRAc",
            "first_name": "some name",
            "last_name": None,
            "user_id": 11,
            "created_at": "2025-10-26T17:14:43.648004",
            "is_verified": False
          }
        }
      },
    },
    **token_responses
  },
)
async def get_me(user: Annotated[UserWithRoles, ValidUserDependency]) -> User:
  return user.user


@users_router.get('/{user_id}', dependencies=[AdminDependency],
  openapi_extra={
    **authorization_header
  },
  responses={
    "200":{
      "model": User,
      "description": "Returns users info by user_id (only with admin credentials)",
      "content": {
        "application/json": {
          "example": {
              "email": "some2@mail.ru",
              "password": "$argon2id$v=19$m=65536,t=3,p=4$RILMC5LB/l/RkFPztO5YIQ$ePFKMnyP3YmMb0EfO4MvXgmj0ew4sm+3UcJEueUVRAc",
              "user_id": 11,
              "created_at": "2025-10-26T17:14:43.648004",
              "is_verified": True
            }
        }
      },
    },
    **token_responses,
    **not_found_responce
  },
)
async def get_user(user_id: int,  session: AsyncSessionDepends) -> User:
  user = await UsersRepository.get_user(session, user_id=user_id)

  if user is None:
    raise HTTPException(detail=f"user {user_id} does not exists", status_code=status.HTTP_404_NOT_FOUND)

  return user


@users_router.delete('/{user_id}', dependencies=[AdminDependency],
  openapi_extra={
    **authorization_header
  },
  responses={
    "200":{
      "model": OKResponce,
      "description": "Returns deleted user's id (only with admin credentials)",
      "content": {
        "application/json": {
          "example": {
              "ok": True,
              "user_id": 1
            }
        }
      },
    },
    **token_responses,
    **not_found_responce
  },
)
async def delete_user(user_id: int, session: AsyncSessionDepends) -> OKResponce:
  result = await UsersRepository.delete_user(session, user_id)

  if result is None:
    raise HTTPException(detail=f"user {user_id} does not exists", status_code=status.HTTP_404_NOT_FOUND)

  return result


@users_router.get('/', dependencies=[AdminDependency],
  openapi_extra={
    **authorization_header
  },
  responses={
    "200":{
      "model": User,
      "description": "Returns all users info (only with admin credentials)",
      "content": {
        "application/json": {
          "example": [
            {
              "email": "some1@mail.ru",
              "password": "$argon2id$v=19$m=65536,t=3,p=4$RILMC5LB/l/RkFPztO5YIQ$ePFKMnyP3YmMb0EfO4MvXgmj0ew4sm+3UcJEueUVRAc",
              "first_name": "some name",
              "last_name": None,
              "user_id": 11,
              "created_at": "2025-10-26T17:14:43.648004",
              "is_verified": False
            },
            {
              "email": "some2@mail.ru",
              "password": "$argon2id$v=19$m=65536,t=3,p=4$RILMC5LB/l/RkFPztO5YIQ$ePFKMnyP3YmMb0EfO4MvXgmj0ew4sm+3UcJEueUVRAc",
              "user_id": 11,
              "created_at": "2025-10-26T17:14:43.648004",
              "is_verified": True
            }
          ]
        }
      },
    },
    **token_responses,
    **not_found_responce
  },
)
async def get_all_users(session: AsyncSessionDepends) -> list[User]:
  result = await UsersRepository.get_users(session)

  if result is None:
    raise HTTPException(detail=f"users not found", status_code=status.HTTP_404_NOT_FOUND)

  return result


@users_router.patch('/{user_id}',
  openapi_extra={
    **authorization_header
  },
  responses={
    "200":{
      "model": OKResponce,
      "description": "Returns partially updated user_id",
      "content": {
        "application/json": {
          "example": {
              "ok": True,
              "user_id": 1
            }
        }
      },
    },
    **token_responses,
    **not_found_responce,
    "400": {
      "description": "Bad Request - Multiple possible errors",
      "content": {
        "access_token_expired": {
          "summary": "access token expired",
          "value": {"detail": "access token expired"}
        },
        "user_exists": {
          "summary": "User already exists",
          "value": {"detail": "User already exists"}
        }
      }
    },
  },
)
async def update_user(
  user_id: int, 
  user: UpdateUser, 
  current_user: Annotated[UserWithRoles, ValidUserDependency], 
  session: AsyncSessionDepends
) -> OKResponce:
  """
    Partially update user:
    
    - **email**: string | None
    - **password**: string | None
    - **first_name**: string | None
    - **last_name**: string | None
  """

  if not is_admin(current_user):
    if current_user.user.user_id != user_id:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
      )
  
  if not user.model_dump(exclude_none=True, exclude_defaults=True):
    raise HTTPException(detail=f"update info not provided", status_code=status.HTTP_400_BAD_REQUEST)

  return await UsersRepository.update_user(session, user_id, user)