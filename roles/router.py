from fastapi import APIRouter, status, HTTPException

from auth.dependencies import AdminDependency
from roles.models import Role
from roles.repository import RolesRepository


roles_router = APIRouter(prefix="/roles", tags=["roles"])


@roles_router.get('/', dependencies=[AdminDependency])
def get_all_roles()->list[Role]:
  result = RolesRepository.get_roles()

  if result is None:
    raise HTTPException(detail=f"roles not found", status_code=status.HTTP_404_NOT_FOUND)

  return result