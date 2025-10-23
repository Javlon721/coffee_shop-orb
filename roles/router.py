from fastapi import APIRouter

from roles.models import Role
from roles.repository import RolesRepository


roles_router = APIRouter(prefix="/roles", tags=["roles"])


@roles_router.get('/')
def get_all_roles()->list[Role]:
  return RolesRepository.get_roles()