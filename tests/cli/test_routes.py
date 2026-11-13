from async_typer import AsyncTyper
from typer.testing import CliRunner

from cli.routes import register_routes


def test_register_routes() -> None:
    app = AsyncTyper()
    register_routes(app)

    runner = CliRunner()
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "storage" in result.stdout
