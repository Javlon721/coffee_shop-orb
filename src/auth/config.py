
from src.utils.models import ConfigModel


class _AuthConfig(ConfigModel):

  #JWT
  JWT_ALGORITHM: str
  JWT_SECRET_KEY: str
  ACCESS_TOKEN_EXPIRE_MINUTES: int
  REFRESH_TOKEN_EXPIRE_HOURS: int

  #Verification
  VERIFICATION_TOKEN_EXPIRE_DAYS: int
  VERIFICATION_TOKEN_BITES_LEN: int
  VERIFICATION_ENDPOINT_PATH: str = "verify"


AuthConfig = _AuthConfig() # type: ignore