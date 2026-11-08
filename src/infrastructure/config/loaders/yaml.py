from pydantic import ValidationError
import yaml
import aiofiles

from infrastructure.config.loaders.base import ConfigLoader
from infrastructure.config.settings import Config
from infrastructure.config.errors import ConfigError


class YamlConfigLoader(ConfigLoader):
    """
    Loads configuration from a YAML file
    """

    def __init__(self, path: str) -> None:
        self.path = path

    async def load(self) -> Config:
        async with aiofiles.open(self.path, "r") as f:
            raw_data = await f.read()

        raw_dict = yaml.safe_load(raw_data) or {}

        try:
            return Config(**raw_dict)
        except ValidationError as e:
            missing_fields = []

            for error in e.errors():
                # error['loc'] is a tuple like ('api', 'url')
                field_path = ".".join(str(x) for x in error["loc"])

                # Check if the error is specifically because a field was missing
                if error["type"] == "missing":
                    missing_fields.append(field_path)

            if missing_fields:
                formatted_list = ", ".join(missing_fields)
                raise ConfigError(
                    f"Missing required configuration fields: {formatted_list}"
                ) from e

            # Fallback for other validation errors (e.g., incorrect type)
            raise ConfigError(f"Configuration validation failed: {e}") from e
