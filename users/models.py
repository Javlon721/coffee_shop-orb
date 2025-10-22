
from datetime import datetime
from pydantic import BaseModel, Field


EMAIL_FIELD = Field(max_length=150, pattern=r"^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
PASSWORD_FIELD = Field(min_length=5, max_length=150)

class RegisterUser(BaseModel):
  email: str = EMAIL_FIELD
  password: str = PASSWORD_FIELD
  first_name: str | None =  Field(default=None, max_length=50)
  last_name: str | None =  Field(default=None, max_length=50)
  
  def set_hashed_password(self, hashed_password: str)->None:
    self.password = hashed_password


class User(RegisterUser):
  user_id: int
  created_at: datetime
  is_verified: bool


class UpdateUser(BaseModel):
  email: str | None = EMAIL_FIELD
  password: str | None = PASSWORD_FIELD
  first_name: str | None =  Field(default=None, max_length=50)
  last_name: str | None =  Field(default=None, max_length=50)


class OKResponce(BaseModel):
  ok: bool
  user_id: int


class UserLogin(BaseModel):
  email: str = EMAIL_FIELD
  password: str = PASSWORD_FIELD
