from db.connection import PsycopgDB
from db.models import DB

from roles.models import Role


class _RolesRepository:

  def __init__(self, db: DB):
    self.db = db


  def get_roles(self) -> list[Role]:
    roles = self.db.query("SELECT * FROM roles")

    return [Role(role_id=role[0], role=role[1]) for role in roles]




RolesRepository = _RolesRepository(PsycopgDB)
