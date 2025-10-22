
from datetime import datetime
from pydantic import BaseModel, Field


class RegisterUser(BaseModel):
  email: str = Field(max_length=150, pattern=r"^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
  password: str =  Field(min_length=5, max_length=150)
  first_name: str | None =  Field(default=None, max_length=50)
  last_name: str | None =  Field(default=None, max_length=50)
  
  def set_hashed_password(self, hashed_password: str)->None:
    self.password = hashed_password


class User(RegisterUser):
  user_id: int
  created_at: datetime
  is_verified: bool


class OKResponce(BaseModel):
  ok: bool
  user_id: int