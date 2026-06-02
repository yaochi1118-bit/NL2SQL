from __future__ import annotations

import json
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

    def save(self, name: str, content: str, tags: list[str] | None = None) -> None:
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
        ddl_dir = self._base / name
        schema_file = ddl_dir / "schema.ddl"
        meta_file = ddl_dir / "meta.json"
        if not schema_file.exists():
            return None
        content = schema_file.read_text(encoding="utf-8")
        if meta_file.exists():
            meta = DDLMeta(**json.loads(meta_file.read_text(encoding="utf-8")))
        else:
            meta = DDLMeta(name=name)
        return content, meta

    def list_all(self) -> list[DDLMeta]:
        if not self._base.exists():
            return []
        results = []
        for ddl_dir in self._base.iterdir():
            if ddl_dir.is_dir():
                meta_file = ddl_dir / "meta.json"
                if meta_file.exists():
                    meta = DDLMeta(**json.loads(meta_file.read_text(encoding="utf-8")))
                else:
                    meta = DDLMeta(name=ddl_dir.name)
                results.append(meta)
        return results

    def delete(self, name: str) -> None:
        ddl_dir = self._base / name
        if not ddl_dir.exists():
            raise FileNotFoundError(f"DDL '{name}' not found.")
        shutil.rmtree(ddl_dir)

    def exists(self, name: str) -> bool:
        return (self._base / name).exists()
