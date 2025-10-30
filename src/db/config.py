

from src.utils.models import ConfigModel


class _DBConfig(ConfigModel):

  POSTGRES_DB: str
  POSTGRES_PASSWORD: str
  DB_USER: str
  DB_HOST: str
  DB_PORT: int
  CONNECTION_POOL_SIZE: int
  CONNECTION_POOL_MAX_SIZE: int
  ORM_ECHO: bool

  ADMIN_EMAIL: str
  ADMIN_PASSWORD: str

  @property
  def URI(self) -> str:
    return f'postgres://{self.DB_USER}:{self.POSTGRES_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}'


  @property
  def DNS(self) -> str:
    return f'postgresql+psycopg://{self.DB_USER}:{self.POSTGRES_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}'


DBConfig = _DBConfig() # type: ignore