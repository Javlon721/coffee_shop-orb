
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, UniqueConstraint

from db.models import CREATED_AT, INT_PK, Base


class UsersRolesORM(Base):
  """
  In some situations `relationship` from sqlalchemy is better choise,
  however i left with simple and brief `join`-usage structure of tables
  """
  
  __tablename__ = "users_roles"

  id: Mapped[INT_PK]
  user_id:  Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"))
  role_id:  Mapped[int] = mapped_column(ForeignKey("roles.role_id", ondelete="CASCADE"))
  created_at: Mapped[CREATED_AT]

  __table_args__ = (UniqueConstraint("user_id", "role_id"), )