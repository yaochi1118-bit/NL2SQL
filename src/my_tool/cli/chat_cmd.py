from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from my_tool.service.chat_service import ChatService

console = Console()

TARGET_DB_CHOICES = ["MySQL", "PostgreSQL", "SQLite", "MaxCompute"]


def get_chat_app(base_path: Path) -> typer.Typer:
    """Build the chat subcommand group."""
    app = typer.Typer(name="chat", help="Chat with your DDL schemas")
    service = ChatService(base_path)

    @app.command()
    def start(
        ddl_name: str = typer.Argument(..., help="Name of the DDL schema"),
        target_db: str | None = typer.Option(
            None, "--target-db", "-d", help="Target database type"
        ),
    ):
        """Start a new chat conversation for a DDL schema."""
        if target_db is None:
            console.print("\n[bold]Select target database:[/bold]")
            for i, db in enumerate(TARGET_DB_CHOICES, 1):
                console.print(f"  [{i}] {db}")
            choice = typer.prompt("Enter number", type=int)
            if choice < 1 or choice > len(TARGET_DB_CHOICES):
                console.print("[red]Invalid selection.[/red]")
                raise typer.Exit(code=1)
            target_db = TARGET_DB_CHOICES[choice - 1]

        try:
            conv = service.create_conversation(ddl_name, target_db)
        except FileNotFoundError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(code=1)

        console.print(
            f"[green]✓[/green] Conversation started! ID: [cyan]{conv.id}[/cyan]"
        )

    @app.command(name="continue")
    def continue_(
        conv_id: str | None = typer.Argument(
            None, help="Conversation ID (default: latest)"
        ),
    ):
        """Continue an existing conversation."""
        conv = None
        if conv_id:
            conv = service.get_conversation(conv_id)
        else:
            conv = service.get_latest_conversation()

        if conv is None:
            console.print("[red]Error: No conversation found.[/red]")
            raise typer.Exit(code=1)

        console.print(f"[bold]Conversation:[/bold] {conv.id}")
        console.print(f"[bold]DDL:[/bold] {conv.ddl_name}")
        console.print(f"[bold]Target DB:[/bold] {conv.target_db}")
        console.print(f"[bold]Messages:[/bold] {conv.message_count}")

        if conv.messages:
            console.print("\n[bold]Previous messages:[/bold]")
            for msg in conv.messages:
                role_tag = (
                    "[cyan]User[/cyan]"
                    if msg.role == "user"
                    else "[green]Assistant[/green]"
                )
                preview = (
                    msg.content[:100] + "..."
                    if len(msg.content) > 100
                    else msg.content
                )
                console.print(f"  {role_tag}: {preview}")

    @app.command()
    def history():
        """List all conversations."""
        convs = service.list_conversations()
        if not convs:
            console.print("[yellow]No conversations found.[/yellow]")
            return

        table = Table(title="Conversations")
        table.add_column("ID", style="cyan")
        table.add_column("DDL Name")
        table.add_column("Target DB")
        table.add_column("Messages", justify="right")
        table.add_column("Created")

        for conv in convs:
            created_str = (
                conv.created_at.strftime("%Y-%m-%d %H:%M:%S")
                if conv.created_at
                else ""
            )
            table.add_row(
                conv.id,
                conv.ddl_name,
                conv.target_db,
                str(conv.message_count),
                created_str,
            )

        console.print(table)

    return app
