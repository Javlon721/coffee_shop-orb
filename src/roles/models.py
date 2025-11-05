from enum import StrEnum

from sqlalchemy.orm import Mapped, mapped_column

from src.db.models import INT_PK, Base


class AvailableRoles(StrEnum):
  ADMIN = "admin"
  USER = "user"


class RolesORM(Base):
  """
  In some situations `relationship` from sqlalchemy is better choise,
  however i left with simple and brief `join`-usage structure of tables
  """
  
  __tablename__ = "roles"
  
  role_id: Mapped[INT_PK]
  role: Mapped[AvailableRoles] = mapped_column(unique=True)