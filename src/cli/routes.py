from async_typer import AsyncTyper
from cli.commands.storage import storage

commands = [storage]


def register_routes(app: AsyncTyper) -> None:
    for command in commands:
        app.add_typer(command)
