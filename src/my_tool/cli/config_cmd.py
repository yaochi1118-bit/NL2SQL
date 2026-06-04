from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from my_tool.service.config_service import ConfigService

console = Console()


def get_config_app(base_path: Path) -> typer.Typer:
    """Build the config subcommand group."""
    app = typer.Typer(name="config", help="Manage LLM configuration")
    service = ConfigService(base_path)

    @app.command()
    def init(
        base_url: str = typer.Option(..., prompt="API Base URL (e.g. https://api.openai.com/v1)"),
        api_key: str = typer.Option(None, "--api-key", "-k", help="API Key"),
        model: str = typer.Option("gpt-4o", prompt="Model name (e.g. gpt-4o, deepseek-chat)"),
    ):
        """Initialize LLM configuration interactively."""
        if api_key is None:
            api_key = input("API Key: ")
        if service.config_exists():
            confirm = typer.confirm("Configuration already exists. Overwrite?")
            if not confirm:
                console.print("[yellow]Cancelled.[/yellow]")
                raise typer.Exit()
        service.init_interactive(base_url=base_url, api_key=api_key, model=model)
        console.print("[green]✓[/green] Configuration created successfully!")

    @app.command()
    def show():
        """Show current LLM configuration (API key masked)."""
        try:
            display = service.show()
        except FileNotFoundError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(code=1)

        table = Table(title="LLM Configuration")
        table.add_column("Key", style="cyan")
        table.add_column("Value")
        for key, value in display.items():
            table.add_row(key, str(value))
        console.print(table)

    @app.command()
    def set(
        key: str = typer.Argument(..., help="Config key (e.g. model, base_url, api_key)"),
        value: str = typer.Argument(..., help="Config value"),
    ):
        """Set a configuration value."""
        try:
            service.set(key, value)
            display_value = value
            if key == "api_key" and len(value) > 8:
                display_value = value[:5] + "***" + value[-3:]
            console.print(f"[green]✓[/green] [bold]{key}[/bold] updated to [cyan]{display_value}[/cyan]")
        except (FileNotFoundError, ValueError) as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(code=1)

    return app
