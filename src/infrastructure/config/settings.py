from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApiConfig(BaseSettings):
    url: str
    csrf_token: str
    meupc_token: str
    model_config = SettingsConfigDict(env_prefix="API_")


class HttpConfig(BaseSettings):
    timeout: int = 3
    retries: int = 3
    rate_limit: int = 10
    model_config = SettingsConfigDict(env_prefix="HTTP_")


class Config(BaseSettings):
    api: ApiConfig
    http: HttpConfig = Field(default_factory=HttpConfig)
    model_config = SettingsConfigDict(env_prefix="")
