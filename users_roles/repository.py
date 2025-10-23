from fastapi import HTTPException, status
from db.connection import PsycopgDB
from db.models import DB
from roles.models import UserRole
from users_roles.models import OKResponce, RegisterUserRole, UserRoles
from psycopg.errors import ForeignKeyViolation, UniqueViolation


class _UsersRolesRepository:

  def __init__(self, db: DB):
    self.db = db


  def get_roles_by(self, user_id: int)-> list[UserRole]:
    roles = self.db.query("SELECT r.role FROM users_roles ur JOIN roles r USING (role_id) WHERE ur.user_id = %s", user_id)
    return [UserRole(role=role[0]) for role in roles]


  def get_all(self) -> list[UserRoles]:
    data = self.db.query("select * from users_roles")
    
    return [UserRoles(id=el[0], user_id=el[1], role_id=el[2], created_at=el[3]) for el in data]


  def add(self, data: RegisterUserRole) -> OKResponce:
    try:
      result = self.db.query_one(
        "INSERT INTO users_roles(user_id, role_id) VALUES (%s, %s) RETURNING id", data.user_id, data.role_id
      )
      
      return OKResponce(ok=True, id=result[0])
    except ForeignKeyViolation:
      raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="ForeignKeyViolation")
    except UniqueViolation:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user already has role")
    except Exception as e:
      raise HTTPException(detail=f"some error occured", status_code=status.HTTP_400_BAD_REQUEST)




UsersRolesRepository = _UsersRolesRepository(PsycopgDB)
