from __future__ import annotations

from pathlib import Path

from my_tool.models import DDLMeta
from my_tool.storage.ddl_store import DDLStore


class DDLService:
    """Business logic layer for DDL schema management.

    Wraps DDLStore with validation and convenience methods.
    """

    def __init__(self, base_path: Path) -> None:
        self._store = DDLStore(base_path / "ddl")

    def add(
        self,
        name: str,
        content: str,
        tags: list[str] | None = None,
        force: bool = False,
    ) -> None:
        """Add a DDL schema with business validation.

        Args:
            name: Name of the DDL schema.
            content: Raw DDL content.
            tags: Optional list of tags.
            force: If True, overwrite existing DDL with the same name.

        Raises:
            ValueError: If content is empty after stripping whitespace.
            FileExistsError: If name already exists and force is False.
        """
        if not content.strip():
            raise ValueError("DDL content cannot be empty.")

        if not force and self._store.exists(name):
            raise FileExistsError(f"DDL '{name}' already exists.")

        self._store.save(name, content, tags=tags)

    def add_from_file(
        self,
        name: str,
        file_path: str,
        tags: list[str] | None = None,
    ) -> None:
        """Read DDL from a file and add it.

        Args:
            name: Name of the DDL schema.
            file_path: Path to the file containing DDL content.
            tags: Optional list of tags.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        content = path.read_text(encoding="utf-8")
        self.add(name, content, tags=tags)

    def list_all(self) -> list[DDLMeta]:
        """List all stored DDL schemas."""
        return self._store.list_all()

    def get(self, name: str) -> tuple[str, DDLMeta] | None:
        """Get a DDL schema by name."""
        return self._store.get(name)

    def delete(self, name: str) -> None:
        """Delete a DDL schema by name."""
        self._store.delete(name)

    def exists(self, name: str) -> bool:
        """Check if a DDL schema exists by name."""
        return self._store.exists(name)
