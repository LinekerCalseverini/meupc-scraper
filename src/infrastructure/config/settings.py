from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from domain.entities.storage.types import StorageInterfaces


class StorageApiConfig(BaseSettings):
    capacity_gb_min: int | None = None
    capacity_gb_max: int | None = None
    storage_interface: StorageInterfaces | None = None
    model_config = SettingsConfigDict(env_prefix="STORAGE_API_")


class ApiConfig(BaseSettings):
    url: str
    storage: StorageApiConfig = Field(default_factory=StorageApiConfig)
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
