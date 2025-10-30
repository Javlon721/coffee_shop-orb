
from src.utils.models import ConfigModel


class _Config(ConfigModel):

  REDIS_HOST: str
  REDIS_PORT: int


  @property
  def URL(self) -> str:
    return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"


Config = _Config() #type: ignore