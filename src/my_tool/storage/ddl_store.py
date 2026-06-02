from __future__ import annotations

import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from my_tool.models import DDLMeta


class DDLStore:
    """File-based storage for DDL schemas.

    Structure:
        ddl/<name>/
            schema.ddl   # raw DDL content
            meta.json    # metadata (name, tags, table_count, created_at)
    """

    def __init__(self, base_path: Path) -> None:
        self._base = base_path

    def _validate_name(self, name: str) -> None:
        """Validate DDL name to prevent path traversal."""
        if not name or name.strip() != name:
            raise ValueError(f"Invalid DDL name: {name!r}")
        if os.path.sep in name or (os.path.altsep and os.path.altsep in name):
            raise ValueError(f"DDL name cannot contain path separators: {name!r}")
        if name in (".", ".."):
            raise ValueError(f"DDL name cannot be '.' or '..'")

    def _load_meta(self, ddl_dir: Path) -> DDLMeta | None:
        """Load DDLMeta from a directory, or None if directory doesn't have schema."""
        schema_file = ddl_dir / "schema.ddl"
        if not schema_file.exists():
            return None
        meta_file = ddl_dir / "meta.json"
        if meta_file.exists():
            return DDLMeta(**json.loads(meta_file.read_text(encoding="utf-8")))
        return DDLMeta(name=ddl_dir.name)

    def save(self, name: str, content: str, tags: list[str] | None = None) -> None:
        self._validate_name(name)
        ddl_dir = self._base / name
        ddl_dir.mkdir(parents=True, exist_ok=True)

        table_count = len(re.findall(r"CREATE\s+TABLE", content, re.IGNORECASE))
        meta = DDLMeta(
            name=name,
            tags=tags or [],
            created_at=datetime.now(timezone.utc),
            table_count=table_count,
        )

        (ddl_dir / "schema.ddl").write_text(content, encoding="utf-8")
        (ddl_dir / "meta.json").write_text(
            meta.model_dump_json(indent=2), encoding="utf-8"
        )

    def get(self, name: str) -> tuple[str, DDLMeta] | None:
        self._validate_name(name)
        ddl_dir = self._base / name
        schema_file = ddl_dir / "schema.ddl"
        meta = self._load_meta(ddl_dir)
        if meta is None:
            return None
        content = schema_file.read_text(encoding="utf-8")
        return content, meta

    def list_all(self) -> list[DDLMeta]:
        if not self._base.exists():
            return []
        results = []
        for ddl_dir in self._base.iterdir():
            if ddl_dir.is_dir():
                meta = self._load_meta(ddl_dir)
                if meta is not None:
                    results.append(meta)
        return results

    def delete(self, name: str) -> None:
        self._validate_name(name)
        ddl_dir = self._base / name
        if not ddl_dir.exists():
            raise FileNotFoundError(f"DDL '{name}' not found.")
        shutil.rmtree(ddl_dir)

    def exists(self, name: str) -> bool:
        self._validate_name(name)
        return (self._base / name).exists()
