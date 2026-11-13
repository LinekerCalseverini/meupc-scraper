import logging

from async_typer import AsyncTyper
from cli.routes import register_routes

logging.basicConfig(level=logging.INFO)


def main() -> None:
    app = AsyncTyper()
    register_routes(app)
    app()
