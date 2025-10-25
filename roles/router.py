from fastapi import APIRouter, status, HTTPException

from auth.dependencies import AdminDependency
from db.connection import AsyncSessionDepends
from roles.models import Role
from roles.repository import RolesRepository


roles_router = APIRouter(prefix="/roles", tags=["roles"])


@roles_router.get('/', dependencies=[AdminDependency])
async def get_all_roles(session: AsyncSessionDepends)->list[Role]:
  result = await RolesRepository.get_roles(session)

  if result is None:
    raise HTTPException(detail=f"roles not found", status_code=status.HTTP_404_NOT_FOUND)

  return result