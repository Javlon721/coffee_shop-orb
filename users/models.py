
from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column

from db.models import CREATED_AT, INT_PK, Base


EMAIL_FIELD = Field(max_length=150, pattern=r"^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
PASSWORD_FIELD = Field(min_length=5, max_length=150)
NAME_FIELD = Field(max_length=50)


class RegisterUser(BaseModel):
  email: Annotated[str, EMAIL_FIELD]
  password:  Annotated[str, PASSWORD_FIELD]
  first_name: Annotated[str | None, NAME_FIELD] = None
  last_name: Annotated[str | None, NAME_FIELD] = None


  def set_hashed_password(self, hashed_password: str)->None:
    self.password = hashed_password


class User(RegisterUser):
  user_id: int
  created_at: datetime
  is_verified: bool


class UserWithRoles(BaseModel):
  user: User
  roles: list[str]


class UpdateUser(BaseModel):
  email: Annotated[str | None, EMAIL_FIELD] = None
  password: Annotated[str | None, PASSWORD_FIELD] = None
  first_name: Annotated[str | None, NAME_FIELD] = None
  last_name: Annotated[str | None, NAME_FIELD] = None


class OKResponce(BaseModel):
  ok: bool
  user_id: int


class UserLogin(BaseModel):
  email: Annotated[str, EMAIL_FIELD]
  password:  Annotated[str, PASSWORD_FIELD]


class UsersORM(Base):
  __tablename__ = "users"
  
  user_id: Mapped[INT_PK]
  email: Mapped[str]
  password: Mapped[str]
  first_name: Mapped[str | None]
  last_name: Mapped[str | None]
  created_at: Mapped[CREATED_AT]
  is_verified: Mapped[bool] = mapped_column(server_default=text("FALSE"))