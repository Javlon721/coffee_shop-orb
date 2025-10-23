
from pydantic import BaseModel


class AccessToken(BaseModel):
  access_token: str
  token_type: str


class RefreshTokens(BaseModel):
  refresh_token: str
  token_type: str


class Tokens(AccessToken, RefreshTokens):
  pass


class AccessTokenData(BaseModel):
  sub: int | None = None
  roles: list[str] = []


class RefreshTokenData(AccessTokenData):
  is_refresh: bool = False