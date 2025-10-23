
from datetime import datetime
from pydantic import BaseModel


class RegisterUserRole(BaseModel):
  user_id: int
  role_id: int


class UserRoles(RegisterUserRole):
  id: int
  created_at: datetime


class OKResponce(BaseModel):
  ok: bool
  id: int