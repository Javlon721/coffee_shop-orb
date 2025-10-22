
from utils.models import ConfigModel


class _AuthConfig(ConfigModel):
  JWT_ALGORITHM: str
  JWT_SECRET_KEY: str
  ACCESS_TOKEN_EXPIRE_MINUTES: int
  REFRESH_TOKEN_EXPIRE_HOURS: int


AuthConfig = _AuthConfig() # type: ignore