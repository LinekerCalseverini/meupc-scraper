from async_typer import AsyncTyper
from cli.routes import register_routes


def main() -> None:
    app = AsyncTyper()
    register_routes(app)
    app()
