from fastapi import HTTPException, status
from psycopg.errors import ForeignKeyViolation, UniqueViolation
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select
from sqlalchemy.orm import aliased
from sqlalchemy.exc import IntegrityError

from roles.models import AvailableRoles, RolesORM, UserRole
from roles.repository import RolesRepository
from users_roles.models import OKResponce, RegisterUserRole, UserRoles, UsersRolesORM


class UsersRolesRepository:
  
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


  @staticmethod
  async def add_default_user_role(session: AsyncSession, user_id: int) -> OKResponce | None:
    default_user_role = AvailableRoles.USER

    resp = await RolesRepository.get_role(session, default_user_role)

    assert resp is not None

    await UsersRolesRepository.add(session, RegisterUserRole(user_id=user_id, role_id=resp.role_id))


  @staticmethod
  async def add_main_admin_roles(session: AsyncSession, user_id: int) -> OKResponce | None:
    admin_role = AvailableRoles.ADMIN

    resp = await RolesRepository.get_role(session, admin_role)

    assert resp is not None

    default_admin_role = RegisterUserRole(user_id=user_id, role_id=resp.role_id)

    result = await UsersRolesRepository.add(session, default_admin_role)

    return result