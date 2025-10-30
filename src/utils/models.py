from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigModel(BaseSettings):

  model_config = SettingsConfigDict(env_file=".env", extra="allow")