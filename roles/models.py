from enum import StrEnum
from pydantic import BaseModel
from sqlalchemy.orm import Mapped, mapped_column

from db.models import INT_PK, Base


class UserRole(BaseModel):
  role: str


class Role(UserRole):
  role_id: int


class AvailableRoles(StrEnum):
  ADMIN = "admin"
  USER = "user"


class RolesORM(Base):
  __tablename__ = "roles"
  
  role_id: Mapped[INT_PK]
  role: Mapped[AvailableRoles] = mapped_column(unique=True)