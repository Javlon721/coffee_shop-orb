from fastapi import APIRouter, status, HTTPException

from src.auth.dependencies import AdminDependency
from src.db.connection import AsyncSessionDepends
from src.roles.schemas import Role
from src.roles.service import RolesService
from src.utils.common_responses import authorization_header, token_responses


roles_router = APIRouter(prefix="/roles", tags=["roles"])


@roles_router.get('/', dependencies=[AdminDependency],
  summary="Get all data from roles table (only for admin)",
  openapi_extra={
    **authorization_header
  },
  responses={
    "200":{
      "model": list[Role],
      "description": "Get all data from roles table (only for admin)",
      "content": {
        "application/json": {
          "example": [
            {
              "role_id": 1,
              "role": "ADMIN"
            },
            {
              "role_id": 2,
              "role": "USER"
            },
          ]
        }
      },
    },
    **token_responses,
    "404": {
    "description": "Not found error",
    "content": {
      "application/json": {
        "example": {"detail": "Roles not found"}
      }
    }
  },
  },
)
async def get_all_roles(session: AsyncSessionDepends)->list[Role]:
  result = await RolesService.get_roles(session)

  if result is None:
    raise HTTPException(detail=f"roles not found", status_code=status.HTTP_404_NOT_FOUND)

  return result