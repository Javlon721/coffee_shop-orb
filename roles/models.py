from pydantic import BaseModel


class UserRole(BaseModel):
  role: str


class Role(UserRole):
  role_id: int