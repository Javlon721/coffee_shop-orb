
from pydantic import BaseModel, field_serializer


class AccessToken(BaseModel):
  access_token: str
  token_type: str


class RefreshTokens(BaseModel):
  refresh_token: str
  token_type: str


class Tokens(AccessToken, RefreshTokens):
  pass


class AccessTokenData(BaseModel):
  user_id: int | None = None
  roles: list[str] = []

  @field_serializer("roles")
  def serialize_roles(self, roles: list[str]) -> str:
    return ' '.join(roles)


class RefreshTokenData(AccessTokenData):
  is_refresh: bool = False