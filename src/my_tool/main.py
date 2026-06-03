from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from my_tool import __version__
from my_tool.cli.chat_cmd import get_chat_app
from my_tool.cli.config_cmd import get_config_app
from my_tool.cli.ddl_cmd import get_ddl_app

console = Console()


def _get_base_path() -> Path:
    """Determine the base path for data storage.

    Uses MY_TOOL_HOME env var if set, otherwise defaults to the current directory.
    """
    import os

    env_home = os.environ.get("MY_TOOL_HOME")
    if env_home:
        return Path(env_home)
    return Path.cwd()


def create_app(base_path: Path | None = None) -> typer.Typer:
    """Create the main Typer application with all subcommands."""
    if base_path is None:
        base_path = _get_base_path()

    app = typer.Typer(
        name="my-tool",
        help="DDL-to-SQL intelligent query tool",
        no_args_is_help=True,
    )

    # Add version option
    def version_callback(value: bool):
        if value:
            console.print(f"my-tool version {__version__}")
            raise typer.Exit()

    @app.callback()
    def main(
        version: bool = typer.Option(
            False,
            "--version",
            "-V",
            help="Show version and exit",
            callback=version_callback,
            is_eager=True,
        ),
    ):
        pass

    # Add subcommands
    app.add_typer(get_config_app(base_path))
    app.add_typer(get_ddl_app(base_path))
    app.add_typer(get_chat_app(base_path))

    return app


app = create_app()


if __name__ == "__main__":
    app()
