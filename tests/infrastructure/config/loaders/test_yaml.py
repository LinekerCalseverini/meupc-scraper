import pytest
from pyfakefs.fake_filesystem import FakeFilesystem
from infrastructure.config.loaders.yaml import YamlConfigLoader
from infrastructure.config.errors import ConfigError


async def test_yaml_config_loader(fs: FakeFilesystem) -> None:
    fs.create_file(
        "config.yaml",
        contents="""
        api:
            url: https://example.com
            csrf_token: abc123
            meupc_token: def456
        http:
            timeout: 10
            retries: 3
            rate_limit: 5
    """,
    )
    loader = YamlConfigLoader("config.yaml")
    config = await loader.load()
    assert config.api.url == "https://example.com"
    assert config.api.csrf_token == "abc123"
    assert config.api.meupc_token == "def456"
    assert config.http.timeout == int(10)
    assert config.http.retries == int(3)
    assert config.http.rate_limit == int(5)


async def test_yaml_config_loader_defaults(fs: FakeFilesystem) -> None:
    fs.create_file(
        "config.yaml",
        contents="""
        api:
            url: https://example.com
            csrf_token: abc123
            meupc_token: def456
    """,
    )
    loader = YamlConfigLoader("config.yaml")
    config = await loader.load()
    assert config.http.timeout == int(3)
    assert config.http.retries == int(3)
    assert config.http.rate_limit == int(10)


async def test_yaml_config_loader_missing_fields(fs: FakeFilesystem) -> None:
    # Create a YAML file missing 'url' and 'csrf_token' under api
    fs.create_file(
        "config.yaml",
        contents="""
        api:
            meupc_token: def456
    """,
    )
    loader = YamlConfigLoader("config.yaml")

    # Assert that ConfigError is raised when loading
    with pytest.raises(ConfigError) as exc_info:
        await loader.load()

    # Verify the error message contains the specific missing fields
    error_message = str(exc_info.value)
    assert "api.url" in error_message
    assert "api.csrf_token" in error_message
