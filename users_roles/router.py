
from fastapi import APIRouter, HTTPException, status

from auth.dependencies import AdminDependency
from db.connection import AsyncSessionDepends
from roles.models import UserRole
from users_roles.models import RegisterUserRole, OKResponce, UserRoles
from users_roles.repository import UsersRolesRepository
from utils.common_responses import authorization_header, token_responses


users_roles_router = APIRouter(prefix="/usersroles", tags=["users_roles"])


not_found_responce = {
  "404": {
    "description": "Not found error",
    "content": {
      "application/json": {
        "example": {"detail": "User roles not found"}
      }
    }
  },
}


@users_roles_router.get('/', dependencies=[AdminDependency],
  summary="Get all data from users_roles table (only for admin)",
  openapi_extra={
    **authorization_header
  },
  responses={
    "200":{
      "model": list[UserRoles],
      "description": "Get all data from users_roles table (only for admin)",
      "content": {
        "application/json": {
          "example": [
            {
              "id": 1,
              "user_id": 1,
              "role_id": 2,
              "created_at": "2025-10-26 17:14:43.695421"
            },
            {
              "id": 2,
              "user_id": 2,
              "role_id": 1,
              "created_at": "2025-15-26 17:14:43.695421"
            },
          ]
        }
      },
    },
    **token_responses,
    **not_found_responce
  },
)
async def get_all(session: AsyncSessionDepends) -> list[UserRoles]:
  result = await UsersRolesRepository.get_all(session)
  
  if result is None:
    raise HTTPException(detail=f"users_roles not found", status_code=status.HTTP_404_NOT_FOUND)
  
  return result


@users_roles_router.get('/{user_id}', dependencies=[AdminDependency],
  summary="Get all user's roles (only for admin)",
  openapi_extra={
    **authorization_header
  },
  responses={
    "200":{
      "model": list[UserRoles],
      "description": "Get all user's roles (only for admin)",
      "content": {
        "application/json": {
          "example": [
            {
              "id": 1,
              "user_id": 1,
              "role_id": 2,
              "created_at": "2025-10-26 17:14:43.695421"
            },
            {
              "id": 2,
              "user_id": 1,
              "role_id": 1,
              "created_at": "2025-15-26 17:14:43.695421"
            },
          ]
        }
      },
    },
    **token_responses,
    **not_found_responce
  },
)
async def get_user_roles(user_id: int, session: AsyncSessionDepends) -> list[UserRole]:
  result = await UsersRolesRepository.get_roles_by(session, user_id)

  if result is None:
    raise HTTPException(detail=f"user roles not found", status_code=status.HTTP_404_NOT_FOUND)

  return result


@users_roles_router.post('/', dependencies=[AdminDependency],
  summary="Add new role for user",
  openapi_extra={
    **authorization_header
  },
  responses={
    "200":{
      "model": OKResponce,
      "description": "Add new role for user",
      "content": {
        "application/json": {
          "example": {
              "ok":True,
              "id": 1
            },
        }
      },
    },
    **token_responses,
    **not_found_responce
  },
)
async def add_role_to_user(data: RegisterUserRole, session: AsyncSessionDepends) -> OKResponce:
  """
    Add new role for user:
    
    - **user_id**: int
    - **role_id**: int
  """

  return await UsersRolesRepository.add(session, data)
