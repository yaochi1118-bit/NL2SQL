from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

from my_tool.service.ddl_service import DDLService

console = Console()


def get_ddl_app(base_path: Path) -> typer.Typer:
    """Build the DDL subcommand group."""
    app = typer.Typer(name="ddl", help="Manage DDL schemas")
    service = DDLService(base_path)

    @app.command()
    def add(
        name: str = typer.Argument(..., help="Name of the DDL schema"),
        file: str | None = typer.Option(None, "--file", "-f", help="Path to DDL file"),
        text: str | None = typer.Option(None, "--text", "-t", help="DDL content as text"),
        tag: list[str] = typer.Option([], "--tag", help="Tags to attach"),
        force: bool = typer.Option(False, "--force", help="Overwrite existing DDL"),
    ):
        """Add a new DDL schema."""
        if file and text:
            console.print("[red]Error: Cannot use both --file and --text simultaneously.[/red]")
            raise typer.Exit(code=1)

        if not file and not text:
            console.print("[red]Error: Either --file or --text must be provided.[/red]")
            raise typer.Exit(code=1)

        try:
            if file:
                service.add_from_file(name, file, tags=tag, force=force)
            else:
                service.add(name, text, tags=tag, force=force)
            console.print(f"[green]OK[/green] DDL '{name}' saved.")
        except (FileNotFoundError, FileExistsError, ValueError) as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(code=1)

    @app.command(name="list")
    def list_():
        """List all uploaded DDL schemas."""
        ddl_list = service.list_all()
        if not ddl_list:
            console.print("[yellow]No DDL schemas found.[/yellow]")
            return

        table = Table(title="DDL Schemas")
        table.add_column("Name", style="cyan")
        table.add_column("Tags")
        table.add_column("Tables", justify="right")
        table.add_column("Created")

        for ddl in ddl_list:
            tags_str = ", ".join(ddl.tags) if ddl.tags else ""
            created_str = ddl.created_at.strftime("%Y-%m-%d %H:%M:%S") if ddl.created_at else ""
            table.add_row(
                ddl.name,
                tags_str,
                str(ddl.table_count),
                created_str,
            )

        console.print(table)

    @app.command()
    def show(
        name: str = typer.Argument(..., help="Name of the DDL schema"),
    ):
        """Show a DDL schema's content."""
        result = service.get(name)
        if result is None:
            console.print(f"[red]Error:[/red] DDL '{name}' not found.")
            raise typer.Exit(code=1)

        content, meta = result

        console.print(f"[bold]Name:[/bold] {meta.name}")
        console.print(f"[bold]Tables:[/bold] {meta.table_count}")
        if meta.tags:
            console.print(f"[bold]Tags:[/bold] {', '.join(meta.tags)}")

        syntax = Syntax(content, "sql", theme="monokai", line_numbers=True)
        console.print(syntax)

    @app.command()
    def delete(
        name: str = typer.Argument(..., help="Name of the DDL schema"),
    ):
        """Delete a DDL schema."""
        try:
            service.delete(name)
            console.print(f"[green]OK[/green] DDL '{name}' deleted.")
        except FileNotFoundError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(code=1)

    return app
