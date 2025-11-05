
from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column

from src.db.models import CREATED_AT, INT_PK, Base


class UsersORM(Base):
  """
  In some situations `relationship` from sqlalchemy is better choise,
  however i left with simple and brief `join`-usage structure of tables
  
  And about database indexes. As we know that postgres event scheduler smart enough 
  to chose correct strategy for searching table's data, I ommited creation of email, or email_password, etc...
  indexes. If we had huge database so i would prefere to chose indexes that can speed up serchings 
  """
  
  __tablename__ = "users"
  
  user_id: Mapped[INT_PK]
  email: Mapped[str] = mapped_column(unique=True)
  password: Mapped[str]
  first_name: Mapped[str | None]
  last_name: Mapped[str | None]
  created_at: Mapped[CREATED_AT]
  is_verified: Mapped[bool] = mapped_column(server_default=text("FALSE"))