from fastapi import HTTPException, status
from psycopg.errors import ForeignKeyViolation, UniqueViolation
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select
from sqlalchemy.orm import aliased
from sqlalchemy.exc import IntegrityError

from db.connection import PsycopgDB
from db.models import DB
from roles.models import RolesORM, UserRole
from users_roles.models import OKResponce, RegisterUserRole, UserRoles, UsersRolesORM


class _UsersRolesRepository:

  def __init__(self, db: DB):
    self.db = db


  def get_roles_by(self, user_id: int) -> list[UserRole] | None:
    roles = self.db.query("SELECT r.role FROM users_roles ur JOIN roles r USING (role_id) WHERE ur.user_id = %s", user_id)

    if not roles:
      return None

    return [UserRole(role=role[0]) for role in roles]


  def get_all(self) -> list[UserRoles] | None:
    data = self.db.query("select * from users_roles")

    if not data:
      return None

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


class UsersRolesRepositoryNew:
  
  @staticmethod
  async def get_roles_by(session: AsyncSession, user_id: int) -> list[UserRole] | None:
    ur = aliased(UsersRolesORM)
    r = aliased(RolesORM)

    query = select(r.role).join(ur, r.role_id == ur.role_id).filter_by(user_id=user_id)

    res = await session.scalars(query)
    result = res.all()

    if not result:
      return None

    return [UserRole(role=role) for role in result]

  @staticmethod
  async def get_all(session: AsyncSession) -> list[UserRoles] | None:
    query = select(UsersRolesORM)

    res = await session.scalars(query)
    result = res.all()

    if not result:
      return None

    return [UserRoles.model_validate(el, from_attributes=True) for el in result]


  @staticmethod
  async def add(session: AsyncSession, data: RegisterUserRole) -> OKResponce:
    try:
      stmt = insert(UsersRolesORM).values(**data.model_dump()).returning(UsersRolesORM.id)

      result = await session.scalar(stmt)

      await session.commit()

      assert result is not None

      return OKResponce(ok=True, id=result)
    except IntegrityError as e:
      match e.orig:
        case ForeignKeyViolation():
          raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="ForeignKeyViolation")
        case UniqueViolation():
          raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user already has role")
        case _:
          raise
    except Exception:
      raise HTTPException(detail=f"some error occured", status_code=status.HTTP_400_BAD_REQUEST)