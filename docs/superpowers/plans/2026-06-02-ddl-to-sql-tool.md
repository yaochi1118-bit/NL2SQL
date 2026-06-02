# DDL-to-SQL 智能查询工具 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a CLI tool that lets users upload DDL schemas and ask natural-language questions to generate SQL queries via LLM.

**Architecture:** Four-layer design — `cli/` (Typer) → `service/` (business logic) → `core/` (LLM + prompt + SQL logic) + `storage/` (file I/O). Fully decoupled layers so API/Web can be added later without rewriting core logic.

**Tech Stack:** Python 3.11, uv build, Typer (CLI), Rich (terminal output), openai SDK (LLM), Pydantic (models/data validation), tomli-w (TOML write), prompt-toolkit (interactive input).

---

### Task 1: Project Setup & Dependencies

**Files:**
- Modify: `pyproject.toml`
- Create: `src/my_tool/__init__.py`
- Create: `src/my_tool/cli/__init__.py`
- Create: `src/my_tool/service/__init__.py`
- Create: `src/my_tool/core/__init__.py`
- Create: `src/my_tool/storage/__init__.py`

- [ ] **Step 1: Update pyproject.toml with dependencies**

```toml
[project]
name = "my-tool"
version = "0.1.0"
description = "DDL-to-SQL intelligent query tool — upload DDL, ask questions in natural language, get SQL"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "typer>=0.12.0",
    "rich>=13.0.0",
    "openai>=1.0.0",
    "pydantic>=2.0.0",
    "tomli-w>=1.0.0",
    "prompt-toolkit>=3.0.0",
]

[project.scripts]
my-tool = "my_tool.main:app"

[build-system]
requires = ["uv_build>=0.11.17,<0.12.0"]
build-backend = "uv_build"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Create package `__init__.py` files**

```python
# src/my_tool/__init__.py
__version__ = "0.1.0"
```

```python
# src/my_tool/cli/__init__.py
```

```python
# src/my_tool/service/__init__.py
```

```python
# src/my_tool/core/__init__.py
```

```python
# src/my_tool/storage/__init__.py
```

- [ ] **Step 3: Install dependencies**

Run: `uv sync`
Expected: All dependencies installed successfully, `.venv` created.

- [ ] **Step 4: Create tests directory and config**

Run: `mkdir -p tests`
Create: `tests/__init__.py` (empty file)

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/ tests/
git commit -m "chore: init project structure and dependencies"
```

---

### Task 2: Data Models (Pydantic)

**Files:**
- Create: `src/my_tool/models.py`

- [ ] **Step 1: Write the failing tests**

Create: `tests/test_models.py`

```python
from my_tool.models import LLMConfig, DDLMeta, Conversation, Message

def test_llm_config_defaults():
    config = LLMConfig(api_key="sk-test", base_url="https://api.openai.com/v1")
    assert config.provider == "openai-compatible"
    assert config.model == "gpt-4o"
    assert config.api_key == "sk-test"

def test_llm_config_no_api_key():
    from pydantic import ValidationError
    import pytest
    with pytest.raises(ValidationError):
        LLMConfig(api_key="", base_url="https://api.openai.com/v1")

def test_ddl_meta_with_tags():
    meta = DDLMeta(name="电商系统", tags=["生产"])
    assert meta.name == "电商系统"
    assert "生产" in meta.tags
    assert meta.table_count == 0

def test_ddl_meta_defaults():
    meta = DDLMeta(name="测试系统")
    assert meta.tags == []
    assert meta.table_count == 0

def test_conversation_create():
    conv = Conversation(
        id="conv-test-1",
        ddl_name="电商系统",
        target_db="PostgreSQL",
        messages=[Message(role="user", content="test")]
    )
    assert conv.message_count == 1
    assert conv.messages[0].role == "user"

def test_conversation_default_updated_at():
    from datetime import datetime
    conv = Conversation(
        id="conv-test-2",
        ddl_name="电商系统",
        target_db="MySQL",
        messages=[]
    )
    assert isinstance(conv.created_at, datetime)
    assert isinstance(conv.updated_at, datetime)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_models.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'my_tool.models'`

- [ ] **Step 3: Write the model implementation**

Create: `src/my_tool/models.py`

```python
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    """LLM provider configuration (OpenAI-compatible API)."""

    provider: str = "openai-compatible"
    base_url: str
    api_key: str = Field(min_length=1)
    model: str = "gpt-4o"


class DDLMeta(BaseModel):
    """Metadata for an uploaded DDL schema."""

    name: str
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    table_count: int = 0


class Message(BaseModel):
    """A single message in a conversation."""

    role: str  # "system" | "user" | "assistant"
    content: str


class Conversation(BaseModel):
    """A chat conversation with history."""

    id: str
    ddl_name: str
    target_db: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    messages: list[Message] = Field(default_factory=list)

    @property
    def message_count(self) -> int:
        return len(self.messages)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_models.py -v`
Expected: All 6 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/my_tool/models.py tests/test_models.py
git commit -m "feat: add Pydantic data models"
```

---

### Task 3: Configuration Module (Storage + Service)

**Files:**
- Create: `src/my_tool/storage/config_store.py`
- Create: `src/my_tool/service/config_service.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Write failing tests**

Create: `tests/test_config.py`

```python
import json
import os
import tempfile
from pathlib import Path

import pytest
from pydantic import ValidationError

from my_tool.models import LLMConfig
from my_tool.storage.config_store import ConfigStore
from my_tool.service.config_service import ConfigService


class TestConfigStore:
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as d:
            yield Path(d)

    def test_save_and_load_config(self, temp_dir):
        store = ConfigStore(temp_dir)
        config = LLMConfig(
            base_url="https://api.deepseek.com/v1",
            api_key="sk-test-key",
            model="deepseek-chat",
        )
        store.save(config)
        loaded = store.load()
        assert loaded.base_url == "https://api.deepseek.com/v1"
        assert loaded.api_key == "sk-test-key"
        assert loaded.model == "deepseek-chat"
        assert loaded.provider == "openai-compatible"

    def test_load_missing_config(self, temp_dir):
        store = ConfigStore(temp_dir)
        assert store.load() is None

    def test_api_key_masked_in_display(self, temp_dir):
        store = ConfigStore(temp_dir)
        config = LLMConfig(
            base_url="https://api.openai.com/v1",
            api_key="sk-abcdefghijklmnop",
        )
        display = store.get_display_dict(config)
        assert "sk-abc***op" in display["api_key"]
        assert "sk-abcdefghijklmnop" not in display["api_key"]


class TestConfigService:
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as d:
            yield Path(d)

    def test_init_interactive_creates_config(self, temp_dir):
        service = ConfigService(temp_dir)
        result = service.init_interactive(
            base_url="https://api.deepseek.com/v1",
            api_key="sk-test",
            model="deepseek-chat",
        )
        assert result is True
        loaded = service.get_config()
        assert loaded.base_url == "https://api.deepseek.com/v1"
        assert loaded.api_key == "sk-test"

    def test_set_config_value(self, temp_dir):
        service = ConfigService(temp_dir)
        service.init_interactive(
            base_url="https://api.openai.com/v1",
            api_key="sk-test",
            model="gpt-4o",
        )
        service.set("model", "gpt-4o-mini")
        loaded = service.get_config()
        assert loaded.model == "gpt-4o-mini"

    def test_get_config_before_init_raises(self, temp_dir):
        service = ConfigService(temp_dir)
        with pytest.raises(FileNotFoundError, match="not initialized"):
            service.get_config()

    def test_config_exists_check(self, temp_dir):
        service = ConfigService(temp_dir)
        assert service.config_exists() is False
        service.init_interactive(
            base_url="https://api.openai.com/v1",
            api_key="sk-test",
        )
        assert service.config_exists() is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_config.py -v`
Expected: FAIL with ModuleNotFoundError

- [ ] **Step 3: Implement ConfigStore**

Create: `src/my_tool/storage/config_store.py`

```python
from __future__ import annotations

from pathlib import Path
from tomllib import TOMLDecodeError

import tomli_w

from my_tool.models import LLMConfig


class ConfigStore:
    """Read/write LLM configuration as config.toml."""

    FILENAME = "config.toml"

    def __init__(self, base_path: Path) -> None:
        self._path = base_path / self.FILENAME

    def save(self, config: LLMConfig) -> None:
        data = {
            "llm": {
                "provider": config.provider,
                "base_url": config.base_url,
                "api_key": config.api_key,
                "model": config.model,
            }
        }
        with open(self._path, "wb") as f:
            tomli_w.dump(data, f)

    def load(self) -> LLMConfig | None:
        if not self._path.exists():
            return None
        try:
            with open(self._path, "rb") as f:
                import tomllib
                data = tomllib.load(f)
            llm = data.get("llm", {})
            return LLMConfig(
                provider=llm.get("provider", "openai-compatible"),
                base_url=llm.get("base_url", ""),
                api_key=llm.get("api_key", ""),
                model=llm.get("model", "gpt-4o"),
            )
        except (TOMLDecodeError, KeyError, ValueError):
            return None

    def get_display_dict(self, config: LLMConfig) -> dict:
        """Return config dict with API key masked for safe display."""
        key = config.api_key
        masked = key[:5] + "***" + key[-3:] if len(key) > 8 else "***"
        return {
            "provider": config.provider,
            "base_url": config.base_url,
            "api_key": masked,
            "model": config.model,
        }
```

- [ ] **Step 4: Implement ConfigService**

Create: `src/my_tool/service/config_service.py`

```python
from __future__ import annotations

from pathlib import Path

from my_tool.models import LLMConfig
from my_tool.storage.config_store import ConfigStore


class ConfigService:
    """Business logic for managing LLM configuration."""

    def __init__(self, base_path: Path) -> None:
        self._store = ConfigStore(base_path)

    def config_exists(self) -> bool:
        return self._store.load() is not None

    def get_config(self) -> LLMConfig:
        config = self._store.load()
        if config is None:
            raise FileNotFoundError(
                "Configuration not initialized. Run `my-tool config init` first."
            )
        return config

    def init_interactive(
        self,
        base_url: str,
        api_key: str,
        model: str = "gpt-4o",
    ) -> bool:
        config = LLMConfig(
            base_url=base_url,
            api_key=api_key,
            model=model,
        )
        self._store.save(config)
        return True

    def set(self, key: str, value: str) -> None:
        config = self.get_config()
        if not hasattr(config, key):
            raise ValueError(f"Unknown config key: {key}")
        setattr(config, key, value)
        self._store.save(config)

    def show(self) -> dict:
        config = self.get_config()
        return self._store.get_display_dict(config)
```

- [ ] **Step 5: Run test to verify it passes**

Run: `uv run pytest tests/test_config.py -v`
Expected: All tests PASS

- [ ] **Step 6: Commit**

```bash
git add src/my_tool/storage/config_store.py src/my_tool/service/config_service.py tests/test_config.py
git commit -m "feat: add config storage and service layer"
```

---

### Task 4: Config CLI Commands

**Files:**
- Create: `src/my_tool/cli/config_cmd.py`
- Create: `tests/test_cli_config.py`

- [ ] **Step 1: Write failing tests**

Create: `tests/test_cli_config.py`

```python
import tempfile
from pathlib import Path
from typer.testing import CliRunner

from my_tool.cli.config_cmd import get_config_app


class TestConfigCLI:
    @pytest.fixture
    def runner(self):
        return CliRunner()

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as d:
            yield Path(d)

    def test_config_init(self, runner, temp_dir):
        app = get_config_app(temp_dir)
        result = runner.invoke(app, [
            "init",
            "--base-url", "https://api.deepseek.com/v1",
            "--api-key", "sk-test-123",
            "--model", "deepseek-chat",
        ])
        assert result.exit_code == 0
        assert "created" in result.stdout.lower()

    def test_config_show(self, runner, temp_dir):
        app = get_config_app(temp_dir)
        runner.invoke(app, [
            "init",
            "--base-url", "https://api.deepseek.com/v1",
            "--api-key", "sk-test-123",
        ])
        result = runner.invoke(app, ["show"])
        assert result.exit_code == 0
        assert "sk-test***123" in result.stdout or "sk-test" in result.stdout

    def test_config_set(self, runner, temp_dir):
        app = get_config_app(temp_dir)
        runner.invoke(app, [
            "init", "--base-url", "https://api.openai.com/v1",
            "--api-key", "sk-test",
        ])
        result = runner.invoke(app, ["set", "model", "gpt-4o-mini"])
        assert result.exit_code == 0
        assert "model" in result.stdout.lower()

    def test_config_show_before_init(self, runner, temp_dir):
        app = get_config_app(temp_dir)
        result = runner.invoke(app, ["show"])
        assert result.exit_code != 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli_config.py -v`
Expected: FAIL with ImportError

- [ ] **Step 3: Write config CLI commands**

Create: `src/my_tool/cli/config_cmd.py`

```python
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
        api_key: str = typer.Option(..., prompt="API Key", hide_input=True),
        model: str = typer.Option("gpt-4o", prompt="Model name (e.g. gpt-4o, deepseek-chat)"),
    ):
        """Initialize LLM configuration interactively."""
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
            console.print(f"[green]✓[/green] [bold]{key}[/bold] updated to [cyan]{value}[/cyan]")
        except (FileNotFoundError, ValueError) as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(code=1)

    return app
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_cli_config.py -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/my_tool/cli/config_cmd.py tests/test_cli_config.py
git commit -m "feat: add config CLI commands"
```

---

### Task 5: DDL Storage Layer

**Files:**
- Create: `src/my_tool/storage/ddl_store.py`
- Create: `tests/test_ddl_store.py`

- [ ] **Step 1: Write failing tests**

Create: `tests/test_ddl_store.py`

```python
import tempfile
from pathlib import Path

import pytest

from my_tool.storage.ddl_store import DDLStore


class TestDDLStore:
    @pytest.fixture
    def store(self):
        with tempfile.TemporaryDirectory() as d:
            yield DDLStore(Path(d) / "ddl")

    def test_save_and_get_ddl(self, store):
        store.save("电商系统", "CREATE TABLE users (id INT);", tags=["生产"])
        content, meta = store.get("电商系统")
        assert "CREATE TABLE users" in content
        assert meta.name == "电商系统"
        assert "生产" in meta.tags

    def test_list_ddls(self, store):
        store.save("电商系统", "DDL A", tags=["生产"])
        store.save("财务系统", "DDL B", tags=["开发"])
        ddl_list = store.list_all()
        assert len(ddl_list) == 2
        names = [m.name for m in ddl_list]
        assert "电商系统" in names
        assert "财务系统" in names

    def test_delete_ddl(self, store):
        store.save("试用系统", "DDL C")
        store.delete("试用系统")
        assert store.get("试用系统") is None

    def test_delete_nonexistent_raises(self, store):
        with pytest.raises(FileNotFoundError):
            store.delete("不存在的系统")

    def test_get_nonexistent_returns_none(self, store):
        assert store.get("不存在的系统") is None

    def test_table_count_in_meta(self, store):
        ddl = """
        CREATE TABLE users (id INT);
        CREATE TABLE orders (id INT);
        CREATE TABLE products (id INT);
        """
        store.save("测试", ddl)
        _, meta = store.get("测试")
        assert meta.table_count == 3

    def test_overwrite_existing(self, store):
        store.save("系统", "OLD DDL")
        store.save("系统", "NEW DDL")
        content, _ = store.get("系统")
        assert content == "NEW DDL"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_ddl_store.py -v`
Expected: FAIL with ModuleNotFoundError

- [ ] **Step 3: Implement DDLStore**

Create: `src/my_tool/storage/ddl_store.py`

```python
from __future__ import annotations

import json
import re
from datetime import datetime
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
            created_at=datetime.now(),
            table_count=table_count,
        )

        (ddl_dir / "schema.ddl").write_text(content, encoding="utf-8")
        (ddl_dir / "meta.json").write_text(
            meta.model_dump_json(indent=2, default=str), encoding="utf-8"
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
        import shutil
        shutil.rmtree(ddl_dir)

    def exists(self, name: str) -> bool:
        return (self._base / name).exists()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_ddl_store.py -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/my_tool/storage/ddl_store.py tests/test_ddl_store.py
git commit -m "feat: add DDL file-based storage layer"
```

---

### Task 6: DDL Service Layer

**Files:**
- Create: `src/my_tool/service/ddl_service.py`
- Create: `tests/test_ddl_service.py`

- [ ] **Step 1: Write failing tests**

Create: `tests/test_ddl_service.py`

```python
import tempfile
from pathlib import Path

import pytest

from my_tool.service.ddl_service import DDLService


class TestDDLService:
    @pytest.fixture
    def service(self):
        with tempfile.TemporaryDirectory() as d:
            yield DDLService(Path(d))

    def test_add_ddl_from_text(self, service):
        service.add("电商系统", "CREATE TABLE users (id INT);", tags=["生产"])
        ddl_list = service.list_all()
        assert len(ddl_list) == 1
        assert ddl_list[0].name == "电商系统"

    def test_add_duplicate_prompt(self, service):
        service.add("系统", "DDL A")
        with pytest.raises(FileExistsError):
            service.add("系统", "DDL B")

    def test_add_duplicate_with_force(self, service):
        service.add("系统", "DDL A")
        service.add("系统", "DDL B", force=True)
        content, _ = service.get("系统")
        assert content == "DDL B"

    def test_add_empty_content_raises(self, service):
        with pytest.raises(ValueError, match="empty"):
            service.add("系统", "")

    def test_add_from_file(self, service):
        with tempfile.TemporaryDirectory() as d:
            file_path = Path(d) / "schema.sql"
            file_path.write_text("CREATE TABLE test (id INT);", encoding="utf-8")
            service.add_from_file("文件导入", str(file_path))
        content, meta = service.get("文件导入")
        assert "CREATE TABLE test" in content

    def test_delete_ddl(self, service):
        service.add("待删除", "CREATE TABLE t (id INT);")
        service.delete("待删除")
        assert service.get("待删除") is None

    def test_get_ddl_detail(self, service):
        service.add("订单系统", "CREATE TABLE orders (id INT);\nCREATE TABLE items (id INT);")
        content, meta = service.get("订单系统")
        assert meta.table_count == 2
        assert "CREATE TABLE orders" in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_ddl_service.py -v`
Expected: FAIL with ModuleNotFoundError

- [ ] **Step 3: Implement DDLService**

Create: `src/my_tool/service/ddl_service.py`

```python
from __future__ import annotations

from pathlib import Path

from my_tool.models import DDLMeta
from my_tool.storage.ddl_store import DDLStore


class DDLService:
    """Business logic for DDL management."""

    def __init__(self, base_path: Path) -> None:
        self._store = DDLStore(base_path / "ddl")

    def add(
        self,
        name: str,
        content: str,
        tags: list[str] | None = None,
        force: bool = False,
    ) -> None:
        if not content.strip():
            raise ValueError("DDL content cannot be empty.")
        if self._store.exists(name) and not force:
            raise FileExistsError(
                f"DDL '{name}' already exists. Use force=True to overwrite."
            )
        self._store.save(name, content, tags=tags)

    def add_from_file(self, name: str, file_path: str, tags: list[str] | None = None) -> None:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        content = path.read_text(encoding="utf-8")
        self.add(name, content, tags=tags, force=False)

    def list_all(self) -> list[DDLMeta]:
        return self._store.list_all()

    def get(self, name: str) -> tuple[str, DDLMeta] | None:
        return self._store.get(name)

    def delete(self, name: str) -> None:
        self._store.delete(name)

    def exists(self, name: str) -> bool:
        return self._store.exists(name)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_ddl_service.py -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/my_tool/service/ddl_service.py tests/test_ddl_service.py
git commit -m "feat: add DDL service layer with business logic"
```

---

### Task 7: DDL CLI Commands

**Files:**
- Create: `src/my_tool/cli/ddl_cmd.py`
- Create: `tests/test_cli_ddl.py`

- [ ] **Step 1: Write failing tests**

Create: `tests/test_cli_ddl.py`

```python
import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from my_tool.cli.ddl_cmd import get_ddl_app


class TestDDLCLI:
    @pytest.fixture
    def runner(self):
        return CliRunner()

    @pytest.fixture
    def app(self):
        with tempfile.TemporaryDirectory() as d:
            yield get_ddl_app(Path(d))

    def test_ddl_add_from_text(self, runner, app):
        result = runner.invoke(app, [
            "add", "电商系统",
            "--text", "CREATE TABLE users (id INT);",
            "--tag", "生产",
        ])
        assert result.exit_code == 0
        assert "saved" in result.stdout.lower()

    def test_ddl_list(self, runner, app):
        runner.invoke(app, ["add", "系统A", "--text", "DDL A"])
        runner.invoke(app, ["add", "系统B", "--text", "DDL B"])
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "系统A" in result.stdout
        assert "系统B" in result.stdout

    def test_ddl_show(self, runner, app):
        runner.invoke(app, ["add", "测试系统", "--text", "CREATE TABLE t (id INT);"])
        result = runner.invoke(app, ["show", "测试系统"])
        assert result.exit_code == 0
        assert "CREATE TABLE t" in result.stdout

    def test_ddl_delete(self, runner, app):
        runner.invoke(app, ["add", "待删除", "--text", "DDL"])
        result = runner.invoke(app, ["delete", "待删除"])
        assert result.exit_code == 0
        assert "deleted" in result.stdout.lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli_ddl.py -v`
Expected: FAIL with ImportError

- [ ] **Step 3: Implement DDL CLI commands**

Create: `src/my_tool/cli/ddl_cmd.py`

```python
from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax

from my_tool.service.ddl_service import DDLService

console = Console()


def get_ddl_app(base_path: Path) -> typer.Typer:
    """Build the ddl subcommand group."""
    app = typer.Typer(name="ddl", help="Manage DDL schemas")
    service = DDLService(base_path)

    @app.command()
    def add(
        name: str = typer.Argument(..., help="Name for the DDL (e.g. 电商系统)"),
        file: str = typer.Option(None, "--file", "-f", help="Path to .sql file"),
        text: str = typer.Option(None, "--text", "-t", help="DDL content as text"),
        tag: list[str] = typer.Option([], "--tag", help="Tag(s) for the DDL (can repeat)"),
        force: bool = typer.Option(False, "--force", help="Overwrite if exists"),
    ):
        """Add a new DDL schema."""
        if file and text:
            console.print("[red]Error:[/red] Provide either --file or --text, not both.")
            raise typer.Exit(code=1)
        if not file and not text:
            console.print("[red]Error:[/red] Provide either --file or --text.")
            raise typer.Exit(code=1)

        try:
            if file:
                service.add_from_file(name, file, tags=tag)
            else:
                service.add(name, text or "", tags=tag, force=force)
            console.print(f"[green]✓[/green] DDL '[bold]{name}[/bold]' saved.")
        except (FileExistsError, FileNotFoundError, ValueError) as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(code=1)

    @app.command()
    def list():
        """List all uploaded DDL schemas."""
        ddl_list = service.list_all()
        if not ddl_list:
            console.print("[yellow]No DDL schemas found. Use `my-tool ddl add` to add one.[/yellow]")
            return

        table = Table(title="DDL Schemas")
        table.add_column("Name", style="cyan")
        table.add_column("Tags", style="green")
        table.add_column("Tables", justify="right")
        table.add_column("Created")
        for meta in ddl_list:
            tags = ", ".join(meta.tags) if meta.tags else "—"
            created = meta.created_at.strftime("%Y-%m-%d %H:%M") if meta.created_at else "—"
            table.add_row(meta.name, tags, str(meta.table_count), created)
        console.print(table)

    @app.command()
    def show(name: str = typer.Argument(..., help="DDL name to display")):
        """Show a DDL schema's content."""
        result = service.get(name)
        if result is None:
            console.print(f"[red]Error:[/red] DDL '{name}' not found.")
            raise typer.Exit(code=1)
        content, meta = result
        console.print(f"[bold]Name:[/bold] {meta.name}")
        console.print(f"[bold]Tables:[/bold] {meta.table_count}")
        console.print(f"[bold]Tags:[/bold] {', '.join(meta.tags) if meta.tags else '—'}")
        console.print()
        syntax = Syntax(content, "sql", theme="monokai", line_numbers=True)
        console.print(syntax)

    @app.command()
    def delete(name: str = typer.Argument(..., help="DDL name to delete")):
        """Delete a DDL schema."""
        try:
            service.delete(name)
            console.print(f"[green]✓[/green] DDL '[bold]{name}[/bold]' deleted.")
        except FileNotFoundError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(code=1)

    return app
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_cli_ddl.py -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/my_tool/cli/ddl_cmd.py tests/test_cli_ddl.py
git commit -m "feat: add DDL CLI commands with Rich tables"
```

---

### Task 8: LLM Client (OpenAI Compatible)

**Files:**
- Create: `src/my_tool/core/llm_client.py`
- Create: `tests/test_llm_client.py`

- [ ] **Step 1: Write failing tests**

Create: `tests/test_llm_client.py`

```python
from unittest.mock import MagicMock, patch

import pytest

from my_tool.models import LLMConfig
from my_tool.core.llm_client import LLMClient


class TestLLMClient:
    @pytest.fixture
    def config(self):
        return LLMConfig(
            base_url="https://api.openai.com/v1",
            api_key="sk-test",
            model="gpt-4o",
        )

    def test_client_initialization(self, config):
        client = LLMClient(config)
        assert client.model == "gpt-4o"

    @patch("my_tool.core.llm_client.OpenAI")
    def test_chat_success(self, mock_openai, config):
        mock_instance = MagicMock()
        mock_openai.return_value = mock_instance
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "SELECT * FROM users;"
        mock_instance.chat.completions.create.return_value = mock_response

        client = LLMClient(config)
        result = client.chat([{"role": "user", "content": "test"}], stream=False)

        assert result == "SELECT * FROM users;"
        mock_instance.chat.completions.create.assert_called_once()

    @patch("my_tool.core.llm_client.OpenAI")
    def test_chat_stream(self, mock_openai, config):
        mock_instance = MagicMock()
        mock_openai.return_value = mock_instance

        # Simulate streaming chunks
        chunk1 = MagicMock()
        chunk1.choices[0].delta.content = "SELECT"
        chunk2 = MagicMock()
        chunk2.choices[0].delta.content = " * FROM"
        chunk3 = MagicMock()
        chunk3.choices[0].delta.content = " users;"

        mock_stream = MagicMock()
        mock_stream.__iter__.return_value = [chunk1, chunk2, chunk3]
        mock_instance.chat.completions.create.return_value = mock_stream

        client = LLMClient(config)
        collected = []
        for chunk in client.chat([{"role": "user", "content": "test"}], stream=True):
            collected.append(chunk)

        full = "".join(collected)
        assert "SELECT * FROM users;" in full

    @patch("my_tool.core.llm_client.OpenAI")
    def test_chat_api_error(self, mock_openai, config):
        from openai import APIError
        mock_instance = MagicMock()
        mock_openai.return_value = mock_instance
        mock_instance.chat.completions.create.side_effect = APIError(
            message="Test error",
            request=MagicMock(),
            body=None,
        )

        client = LLMClient(config)
        with pytest.raises(APIError):
            client.chat([{"role": "user", "content": "test"}], stream=False)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_llm_client.py -v`
Expected: FAIL with ModuleNotFoundError

- [ ] **Step 3: Implement LLMClient**

Create: `src/my_tool/core/llm_client.py`

```python
from __future__ import annotations

from collections.abc import Generator

from openai import OpenAI

from my_tool.models import LLMConfig


class LLMClient:
    """OpenAI-compatible API client for LLM interactions."""

    def __init__(self, config: LLMConfig) -> None:
        self._client = OpenAI(
            base_url=config.base_url,
            api_key=config.api_key,
        )
        self.model = config.model

    def chat(
        self,
        messages: list[dict],
        stream: bool = True,
    ) -> str | Generator[str, None, None]:
        """Send a chat completion request.

        If stream=True, returns a generator yielding content chunks.
        If stream=False, returns the full response string.
        """
        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=stream,
        )

        if stream:

            def generate() -> Generator[str, None, None]:
                for chunk in response:
                    delta = chunk.choices[0].delta if chunk.choices else None
                    if delta and delta.content:
                        yield delta.content

            return generate()
        else:
            return response.choices[0].message.content or ""
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_llm_client.py -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/my_tool/core/llm_client.py tests/test_llm_client.py
git commit -m "feat: add OpenAI-compatible LLM client with streaming"
```

---

### Task 9: Prompt Builder

**Files:**
- Create: `src/my_tool/core/prompt_builder.py`
- Create: `tests/test_prompt_builder.py`

- [ ] **Step 1: Write failing tests**

Create: `tests/test_prompt_builder.py`

```python
from my_tool.core.prompt_builder import PromptBuilder


class TestPromptBuilder:
    def test_build_system_prompt(self):
        ddl_content = "CREATE TABLE users (id INT);\nCREATE TABLE orders (id INT);"
        prompt = PromptBuilder.build_system_prompt(
            ddl_content=ddl_content,
            target_db="PostgreSQL",
        )
        assert "PostgreSQL" in prompt
        assert "CREATE TABLE users" in prompt
        assert "CREATE TABLE orders" in prompt
        assert "SQL 生成助手" in prompt

    def test_build_system_prompt_mysql(self):
        ddl_content = "CREATE TABLE products (id INT);"
        prompt = PromptBuilder.build_system_prompt(ddl_content, "MySQL")
        assert "MySQL" in prompt
        assert "products" in prompt

    def test_build_messages(self):
        ddl = "CREATE TABLE t (id INT);"
        system_prompt = PromptBuilder.build_system_prompt(ddl, "SQLite")
        messages = PromptBuilder.build_messages(
            system_prompt=system_prompt,
            history=[
                {"role": "user", "content": "第一个问题"},
                {"role": "assistant", "content": "第一个回答"},
            ],
            new_question="追问",
        )
        assert len(messages) == 3
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert messages[2]["role"] == "user"
        assert messages[2]["content"] == "追问"

    def test_build_messages_no_history(self):
        ddl = "CREATE TABLE t (id INT);"
        system_prompt = PromptBuilder.build_system_prompt(ddl, "MySQL")
        messages = PromptBuilder.build_messages(
            system_prompt=system_prompt,
            history=[],
            new_question="第一个问题",
        )
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_prompt_builder.py -v`
Expected: FAIL with ModuleNotFoundError

- [ ] **Step 3: Implement PromptBuilder**

Create: `src/my_tool/core/prompt_builder.py`

```python
from __future__ import annotations

from my_tool.models import Message


class PromptBuilder:
    """Build prompts for LLM SQL generation."""

    SYSTEM_PROMPT_TEMPLATE = """你是一个 SQL 生成助手。根据用户提供的数据库 DDL 和自然语言问题，生成对应的 SQL 查询语句。

目标数据库方言：{target_db}

以下是 DDL 定义：
{ddl_content}

要求：
1. 只输出可执行的 SQL 语句
2. 用自然语言简要解释 SQL 的逻辑
3. 如果问题有歧义，说明你的假设
4. SQL 必须与目标数据库方言兼容"""

    @classmethod
    def build_system_prompt(cls, ddl_content: str, target_db: str) -> str:
        """Build the system prompt with DDL context."""
        return cls.SYSTEM_PROMPT_TEMPLATE.format(
            target_db=target_db,
            ddl_content=ddl_content,
        )

    @classmethod
    def build_messages(
        cls,
        system_prompt: str,
        history: list[dict],
        new_question: str,
    ) -> list[dict]:
        """Build the full messages array for the LLM API call.

        Args:
            system_prompt: The system prompt with DDL context.
            history: Previous conversation messages (without system prompt).
            new_question: The user's new question.
        """
        messages: list[dict] = [{"role": "system", "content": system_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": new_question})
        return messages
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_prompt_builder.py -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/my_tool/core/prompt_builder.py tests/test_prompt_builder.py
git commit -m "feat: add prompt builder for SQL generation"
```

---

### Task 10: SQL Parser

**Files:**
- Create: `src/my_tool/core/sql_parser.py`
- Create: `tests/test_sql_parser.py`

- [ ] **Step 1: Write failing tests**

Create: `tests/test_sql_parser.py`

```python
from my_tool.core.sql_parser import SQLParser


class TestSQLParser:
    def test_extract_sql_from_code_block(self):
        text = "```sql\nSELECT * FROM users;\n```"
        assert SQLParser.extract_sql(text) == "SELECT * FROM users;"

    def test_extract_sql_with_explanation(self):
        text = """Here's the query you need:
```sql
SELECT u.name, COUNT(o.id) as order_count
FROM users u
JOIN orders o ON u.id = o.user_id
GROUP BY u.name
ORDER BY order_count DESC
LIMIT 10;
```
This will show the top 10 users by order count."""
        result = SQLParser.extract_sql(text)
        assert "SELECT u.name" in result
        assert "LIMIT 10" in result
        assert "Here's the query" not in result

    def test_extract_sql_plain_text(self):
        text = "SELECT * FROM users;"
        assert SQLParser.extract_sql(text) == "SELECT * FROM users;"

    def test_extract_sql_multiple_code_blocks(self):
        text = "First:\n```sql\nSELECT 1;\n```\nSecond:\n```sql\nSELECT 2;\n```"
        # Should return the first block
        assert SQLParser.extract_sql(text) == "SELECT 1;"

    def test_extract_sql_no_sql_found(self):
        text = "I don't know how to answer that question."
        assert SQLParser.extract_sql(text) == ""

    def test_validate_basic_valid_select(self):
        assert SQLParser.validate_sql_basic("SELECT * FROM users WHERE id = 1;", "MySQL") is True

    def test_validate_basic_valid_with_cte(self):
        assert SQLParser.validate_sql_basic(
            "WITH cte AS (SELECT * FROM users) SELECT * FROM cte;", "PostgreSQL"
        ) is True

    def test_validate_basic_empty(self):
        assert SQLParser.validate_sql_basic("", "MySQL") is False
        assert SQLParser.validate_sql_basic("   ", "SQLite") is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_sql_parser.py -v`
Expected: FAIL with ModuleNotFoundError

- [ ] **Step 3: Implement SQLParser**

Create: `src/my_tool/core/sql_parser.py`

```python
from __future__ import annotations

import re


class SQLParser:
    """Extract and validate SQL from LLM responses."""

    SQL_KEYWORDS = {"SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "WITH", "EXPLAIN"}

    @classmethod
    def extract_sql(cls, text: str) -> str:
        """Extract SQL from LLM response, stripping Markdown and explanation text.

        Priority:
        1. First ```sql ... ``` code block
        2. First ``` ... ``` code block
        3. Plain text starting with an SQL keyword
        4. Empty string
        """
        # Try ```sql ... ``` block first
        match = re.search(r"```sql\s*\n(.*?)\n```", text, re.DOTALL)
        if match:
            return match.group(1).strip()

        # Try ``` ... ``` block
        match = re.search(r"```\s*\n(.*?)\n```", text, re.DOTALL)
        if match:
            return match.group(1).strip()

        # Check if the text itself is SQL-like
        stripped = text.strip()
        if stripped and cls._looks_like_sql(stripped):
            return stripped

        return ""

    @classmethod
    def _looks_like_sql(cls, text: str) -> bool:
        """Check if text starts with a known SQL keyword."""
        first_word = text.split()[0].upper() if text.split() else ""
        return first_word in cls.SQL_KEYWORDS

    @classmethod
    def validate_sql_basic(cls, sql: str, db_type: str) -> bool:
        """Basic SQL validation — checks if it's non-empty and starts with a known keyword."""
        stripped = sql.strip()
        if not stripped:
            return False
        return cls._looks_like_sql(stripped)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_sql_parser.py -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/my_tool/core/sql_parser.py tests/test_sql_parser.py
git commit -m "feat: add SQL parser for extracting and validating SQL from LLM responses"
```

---

### Task 11: Conversation Storage

**Files:**
- Create: `src/my_tool/storage/conversation_store.py`
- Create: `tests/test_conversation_store.py`

- [ ] **Step 1: Write failing tests**

Create: `tests/test_conversation_store.py`

```python
import tempfile
from pathlib import Path

import pytest

from my_tool.models import Conversation, Message
from my_tool.storage.conversation_store import ConversationStore


class TestConversationStore:
    @pytest.fixture
    def store(self):
        with tempfile.TemporaryDirectory() as d:
            yield ConversationStore(Path(d) / "conversations")

    def test_save_and_get_conversation(self, store):
        conv = Conversation(
            id="conv-test-1",
            ddl_name="电商系统",
            target_db="PostgreSQL",
            messages=[Message(role="user", content="test")],
        )
        store.save(conv)
        loaded = store.get("conv-test-1")
        assert loaded is not None
        assert loaded.id == "conv-test-1"
        assert loaded.ddl_name == "电商系统"
        assert loaded.message_count == 1

    def test_get_latest(self, store):
        conv1 = Conversation(id="conv-old", ddl_name="A", target_db="MySQL", messages=[])
        conv2 = Conversation(id="conv-new", ddl_name="B", target_db="PG", messages=[])
        store.save(conv1)
        store.save(conv2)
        latest = store.get_latest()
        assert latest is not None
        assert latest.id == "conv-new"

    def test_get_latest_empty(self, store):
        assert store.get_latest() is None

    def test_list_all(self, store):
        store.save(Conversation(id="c1", ddl_name="A", target_db="M", messages=[]))
        store.save(Conversation(id="c2", ddl_name="B", target_db="P", messages=[]))
        conv_list = store.list_all()
        assert len(conv_list) == 2

    def test_delete(self, store):
        store.save(Conversation(id="c-del", ddl_name="X", target_db="Y", messages=[]))
        store.delete("c-del")
        assert store.get("c-del") is None

    def test_update_existing(self, store):
        conv = Conversation(id="c-upd", ddl_name="S", target_db="SQLite", messages=[])
        store.save(conv)
        conv.messages.append(Message(role="user", content="new msg"))
        store.save(conv)
        loaded = store.get("c-upd")
        assert loaded is not None
        assert loaded.message_count == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_conversation_store.py -v`
Expected: FAIL with ModuleNotFoundError

- [ ] **Step 3: Implement ConversationStore**

Create: `src/my_tool/storage/conversation_store.py`

```python
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from my_tool.models import Conversation, Message


class ConversationStore:
    """File-based storage for conversation history.

    Each conversation is stored as:
        conversations/conv-<id>.json
    """

    def __init__(self, base_path: Path) -> None:
        self._base = base_path
        self._base.mkdir(parents=True, exist_ok=True)

    def save(self, conversation: Conversation) -> None:
        conversation.updated_at = datetime.now()
        file_path = self._base / f"{conversation.id}.json"
        file_path.write_text(
            conversation.model_dump_json(indent=2, default=str),
            encoding="utf-8",
        )

    def get(self, conv_id: str) -> Optional[Conversation]:
        file_path = self._base / f"{conv_id}.json"
        if not file_path.exists():
            return None
        data = json.loads(file_path.read_text(encoding="utf-8"))
        messages = [Message(**m) for m in data.get("messages", [])]
        return Conversation(**{**data, "messages": messages})

    def get_latest(self) -> Optional[Conversation]:
        if not self._base.exists():
            return None
        json_files = sorted(self._base.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
        if not json_files:
            return None
        return self.get(json_files[0].stem)

    def list_all(self) -> list[Conversation]:
        if not self._base.exists():
            return []
        convs = []
        for f in sorted(self._base.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True):
            conv = self.get(f.stem)
            if conv:
                convs.append(conv)
        return convs

    def delete(self, conv_id: str) -> None:
        file_path = self._base / f"{conv_id}.json"
        if file_path.exists():
            file_path.unlink()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_conversation_store.py -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/my_tool/storage/conversation_store.py tests/test_conversation_store.py
git commit -m "feat: add conversation storage with history management"
```

---

### Task 12: Chat Service

**Files:**
- Create: `src/my_tool/service/chat_service.py`
- Create: `tests/test_chat_service.py`

- [ ] **Step 1: Write failing tests**

Create: `tests/test_chat_service.py`

```python
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from my_tool.models import LLMConfig, Conversation, Message
from my_tool.service.chat_service import ChatService
from my_tool.service.config_service import ConfigService
from my_tool.service.ddl_service import DDLService


class TestChatService:
    @pytest.fixture
    def chat_service(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            # Initialize config
            ConfigService(base).init_interactive(
                base_url="https://api.openai.com/v1",
                api_key="sk-test",
            )
            # Add a DDL
            DDLService(base).add("电商系统", "CREATE TABLE users (id INT);")
            yield ChatService(base)

    def test_create_conversation(self, chat_service):
        conv = chat_service.create_conversation("电商系统", "PostgreSQL")
        assert conv.ddl_name == "电商系统"
        assert conv.target_db == "PostgreSQL"
        assert conv.id.startswith("conv-")

    def test_create_conversation_nonexistent_ddl(self, chat_service):
        with pytest.raises(FileNotFoundError):
            chat_service.create_conversation("不存在的系统", "MySQL")

    @patch("my_tool.core.llm_client.LLMClient.chat")
    def test_ask_question(self, mock_chat, chat_service):
        mock_chat.return_value = "```sql\nSELECT * FROM users;\n```"
        conv = chat_service.create_conversation("电商系统", "PostgreSQL")
        result = chat_service.ask(conv.id, "查询所有用户")

        assert result["sql"] == "SELECT * FROM users;"
        assert "sql" in result
        assert len(result["messages"]) == 3  # system + user + assistant

    def test_ask_in_nonexistent_conversation(self, chat_service):
        with pytest.raises(FileNotFoundError):
            chat_service.ask("conv-nonexistent", "test")

    def test_ask_without_init(self, chat_service):
        chat_service._config_service = ConfigService(Path("/nonexistent"))
        with pytest.raises(FileNotFoundError):
            chat_service.ask("any", "test")

    def test_get_conversation(self, chat_service):
        conv = chat_service.create_conversation("电商系统", "MySQL")
        loaded = chat_service.get_conversation(conv.id)
        assert loaded is not None
        assert loaded.id == conv.id

    def test_list_conversations(self, chat_service):
        chat_service.create_conversation("电商系统", "PG")
        chat_service.create_conversation("电商系统", "MySQL")
        convs = chat_service.list_conversations()
        assert len(convs) == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_chat_service.py -v`
Expected: FAIL with ModuleNotFoundError

- [ ] **Step 3: Implement ChatService**

Create: `src/my_tool/service/chat_service.py`

```python
from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from my_tool.core.llm_client import LLMClient
from my_tool.core.prompt_builder import PromptBuilder
from my_tool.core.sql_parser import SQLParser
from my_tool.models import Conversation, LLMConfig, Message
from my_tool.service.config_service import ConfigService
from my_tool.service.ddl_service import DDLService
from my_tool.storage.conversation_store import ConversationStore


class ChatService:
    """Business logic for chat/SQL generation conversations."""

    def __init__(self, base_path: Path) -> None:
        self._config_service = ConfigService(base_path)
        self._ddl_service = DDLService(base_path)
        self._conv_store = ConversationStore(base_path / "conversations")

    def create_conversation(self, ddl_name: str, target_db: str) -> Conversation:
        """Create a new conversation for a given DDL."""
        if not self._ddl_service.exists(ddl_name):
            raise FileNotFoundError(f"DDL '{ddl_name}' not found.")

        conv_id = f"conv-{datetime.now().strftime('%Y%m%d')}-{ddl_name}-{uuid.uuid4().hex[:6]}"
        conv = Conversation(
            id=conv_id,
            ddl_name=ddl_name,
            target_db=target_db,
            messages=[],
        )
        self._conv_store.save(conv)
        return conv

    def ask(self, conv_id: str, question: str) -> dict:
        """Ask a question in an existing conversation.

        Returns:
            dict with keys: sql (str), explanation (str), messages (list)
        """
        conv = self._conv_store.get(conv_id)
        if conv is None:
            raise FileNotFoundError(f"Conversation '{conv_id}' not found.")

        # Get DDL content
        ddl_result = self._ddl_service.get(conv.ddl_name)
        if ddl_result is None:
            raise FileNotFoundError(f"DDL '{conv.ddl_name}' not found.")
        ddl_content, _ = ddl_result

        # Build prompt
        system_prompt = PromptBuilder.build_system_prompt(ddl_content, conv.target_db)
        history = [{"role": m.role, "content": m.content} for m in conv.messages]
        messages = PromptBuilder.build_messages(system_prompt, history, question)

        # Call LLM
        config = self._config_service.get_config()
        client = LLMClient(config)
        response = client.chat(messages, stream=False)
        if isinstance(response, str):
            raw_response = response
        else:
            raw_response = "".join(list(response))

        # Parse SQL
        sql = SQLParser.extract_sql(raw_response)
        valid = SQLParser.validate_sql_basic(sql, conv.target_db)

        # Extract explanation (everything after the SQL block)
        explanation = raw_response
        if "```" in raw_response:
            parts = raw_response.split("```")
            if len(parts) > 2:
                explanation = parts[-1].strip() or ""

        # Save messages
        conv.messages.append(Message(role="user", content=question))
        conv.messages.append(Message(role="assistant", content=raw_response))
        self._conv_store.save(conv)

        return {
            "sql": sql if valid else "",
            "raw_response": raw_response,
            "explanation": explanation,
            "valid": valid,
            "messages": conv.messages,
        }

    def get_conversation(self, conv_id: str) -> Optional[Conversation]:
        return self._conv_store.get(conv_id)

    def get_latest_conversation(self) -> Optional[Conversation]:
        return self._conv_store.get_latest()

    def list_conversations(self) -> list[Conversation]:
        return self._conv_store.list_all()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_chat_service.py -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/my_tool/service/chat_service.py tests/test_chat_service.py
git commit -m "feat: add chat service for SQL generation conversations"
```

---

### Task 13: Chat CLI Commands

**Files:**
- Create: `src/my_tool/cli/chat_cmd.py`
- Create: `tests/test_cli_chat.py`

- [ ] **Step 1: Write failing tests**

Create: `tests/test_cli_chat.py`

```python
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from my_tool.cli.chat_cmd import get_chat_app
from my_tool.service.config_service import ConfigService
from my_tool.service.ddl_service import DDLService


class TestChatCLI:
    @pytest.fixture
    def runner(self):
        return CliRunner()

    @pytest.fixture
    def app(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            ConfigService(base).init_interactive(
                base_url="https://api.openai.com/v1",
                api_key="sk-test",
            )
            DDLService(base).add("电商系统", "CREATE TABLE users (id INT);")
            yield get_chat_app(base)

    def test_chat_start(self, runner, app):
        result = runner.invoke(app, ["start", "电商系统", "--target-db", "PostgreSQL"])
        assert result.exit_code == 0
        assert "started" in result.stdout.lower()

    def test_chat_start_nonexistent_ddl(self, runner, app):
        result = runner.invoke(app, ["start", "不存在", "--target-db", "MySQL"])
        assert result.exit_code != 0

    def test_chat_history_empty(self, runner, app):
        result = runner.invoke(app, ["history"])
        assert result.exit_code == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli_chat.py -v`
Expected: FAIL with ImportError

- [ ] **Step 3: Implement Chat CLI commands**

Create: `src/my_tool/cli/chat_cmd.py`

```python
from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.prompt import Prompt

from my_tool.service.chat_service import ChatService

console = Console()

TARGET_DB_CHOICES = ["MySQL", "PostgreSQL", "SQLite", "MaxCompute"]


def get_chat_app(base_path: Path) -> typer.Typer:
    """Build the chat subcommand group."""
    app = typer.Typer(name="chat", help="Chat to generate SQL from DDL")
    service = ChatService(base_path)

    @app.command()
    def start(
        ddl_name: str = typer.Argument(..., help="DDL name to chat about"),
        target_db: str = typer.Option(
            None,
            "--target-db",
            help=f"Target database: {', '.join(TARGET_DB_CHOICES)}",
        ),
    ):
        """Start a new chat conversation for a DDL."""
        if target_db and target_db not in TARGET_DB_CHOICES:
            console.print(f"[red]Error:[/red] Unsupported database. Choose from: {', '.join(TARGET_DB_CHOICES)}")
            raise typer.Exit(code=1)

        if not target_db:
            console.print("[bold]Select target database:[/bold]")
            for i, db in enumerate(TARGET_DB_CHOICES, 1):
                console.print(f"  {i}. {db}")
            choice = Prompt.ask("Enter number", choices=[str(i) for i in range(1, len(TARGET_DB_CHOICES) + 1)])
            target_db = TARGET_DB_CHOICES[int(choice) - 1]

        try:
            conv = service.create_conversation(ddl_name, target_db)
            console.print(f"[green]✓[/green] Conversation started! (ID: [cyan]{conv.id}[/cyan])")
            console.print(f"[dim]DDL: {ddl_name} | Target: {target_db}[/dim]")
            console.print()
            _interactive_chat(service, conv.id)
        except FileNotFoundError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(code=1)

    @app.command()
    def continue_(
        conv_id: str = typer.Argument(
            None,
            help="Conversation ID to continue (default: latest)",
        ),
    ):
        """Continue an existing conversation."""
        if conv_id:
            conv = service.get_conversation(conv_id)
        else:
            conv = service.get_latest_conversation()

        if conv is None:
            console.print("[yellow]No conversations found. Use `my-tool chat start` to begin.[/yellow]")
            raise typer.Exit(code=1)

        console.print(f"[green]✓[/green] Continuing conversation [cyan]{conv.id}[/cyan]")
        console.print(f"[dim]DDL: {conv.ddl_name} | Target: {conv.target_db}[/dim]")
        console.print()

        # Show previous messages
        for msg in conv.messages:
            if msg.role == "user":
                console.print(Panel(f"[bold]You:[/bold] {msg.content}", style="blue"))
            elif msg.role == "assistant":
                sql = _extract_sql_preview(msg.content)
                console.print(Panel(f"[bold]AI:[/bold]\n{sql}", style="green"))

        _interactive_chat(service, conv.id)

    @app.command()
    def history():
        """List all conversation history."""
        convs = service.list_conversations()
        if not convs:
            console.print("[yellow]No conversation history.[/yellow]")
            return

        table = Table(title="Conversation History")
        table.add_column("ID", style="cyan")
        table.add_column("DDL", style="green")
        table.add_column("Target DB")
        table.add_column("Messages", justify="right")
        table.add_column("Last Updated")
        for conv in convs:
            table.add_row(
                conv.id,
                conv.ddl_name,
                conv.target_db,
                str(conv.message_count),
                conv.updated_at.strftime("%Y-%m-%d %H:%M"),
            )
        console.print(table)

    def _interactive_chat(service: ChatService, conv_id: str) -> None:
        """Interactive chat loop."""
        console.print("[dim]Enter your question (or /exit to quit, /help for commands)[/dim]")
        console.print()

        from prompt_toolkit import PromptSession
        session = PromptSession()

        while True:
            try:
                question = session.prompt("> ")
            except (EOFError, KeyboardInterrupt):
                console.print("\n[yellow]Exiting chat.[/yellow]")
                break

            if not question.strip():
                continue

            if question.strip().lower() == "/exit":
                console.print("[yellow]Exiting chat. Use `my-tool chat continue` to resume.[/yellow]")
                break

            if question.strip().lower() == "/help":
                console.print("[bold]Commands:[/bold]")
                console.print("  /exit  - Exit current chat")
                console.print("  /help  - Show this help")
                continue

            with console.status("[bold green]Generating SQL...[/bold green]"):
                try:
                    result = service.ask(conv_id, question)
                except Exception as e:
                    console.print(f"[red]Error:[/red] {e}")
                    continue

            if result["valid"]:
                syntax = Syntax(result["sql"], "sql", theme="monokai")
                console.print(Panel(syntax, title="SQL", border_style="green"))
            else:
                console.print("[yellow]Could not extract valid SQL from the response.[/yellow]")

            if result["explanation"]:
                console.print(Panel(result["explanation"], title="Explanation", border_style="blue"))

            console.print()

    def _extract_sql_preview(text: str) -> str:
        """Extract just the SQL portion for preview display."""
        import re
        match = re.search(r"```sql\s*\n(.*?)\n```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text[:200] + "..." if len(text) > 200 else text

    return app
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_cli_chat.py -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/my_tool/cli/chat_cmd.py tests/test_cli_chat.py
git commit -m "feat: add chat CLI commands with interactive mode"
```

---

### Task 14: Main CLI Entry Point

**Files:**
- Create: `src/my_tool/main.py`
- Create: `tests/test_main.py`

- [ ] **Step 1: Write failing tests**

Create: `tests/test_main.py`

```python
import tempfile
from pathlib import Path

from typer.testing import CliRunner

from my_tool.main import create_app


class TestMainCLI:
    @pytest.fixture
    def runner(self):
        return CliRunner()

    @pytest.fixture
    def app(self):
        with tempfile.TemporaryDirectory() as d:
            yield create_app(Path(d))

    def test_help(self, runner, app):
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "config" in result.stdout
        assert "ddl" in result.stdout
        assert "chat" in result.stdout

    def test_version(self, runner, app):
        # Add a --version option
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0

    def test_config_subcommand_visible(self, runner, app):
        result = runner.invoke(app, ["config", "--help"])
        assert result.exit_code == 0

    def test_ddl_subcommand_visible(self, runner, app):
        result = runner.invoke(app, ["ddl", "--help"])
        assert result.exit_code == 0

    def test_chat_subcommand_visible(self, runner, app):
        result = runner.invoke(app, ["chat", "--help"])
        assert result.exit_code == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_main.py -v`
Expected: FAIL with ModuleNotFoundError

- [ ] **Step 3: Implement main entry point**

Create: `src/my_tool/main.py`

```python
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
            False, "--version", "-V",
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_main.py -v`
Expected: All tests PASS

- [ ] **Step 5: Verify CLI works end-to-end**

Run: `uv run my-tool --help`
Expected: Shows help with config, ddl, chat subcommands

- [ ] **Step 6: Commit**

```bash
git add src/my_tool/main.py tests/test_main.py
git commit -m "feat: add main CLI entry point with all subcommands"
```

---

### Task 15: Integration Smoke Test

**Files:**
- Create: `tests/test_integration.py`

- [ ] **Step 1: Write integration smoke test**

Create: `tests/test_integration.py`

```python
"""Smoke test — exercises the full flow: config init → ddl add → chat start."""
import tempfile
from pathlib import Path

from typer.testing import CliRunner

from my_tool.main import create_app


class TestIntegration:
    @pytest.fixture
    def runner(self):
        return CliRunner()

    @pytest.fixture
    def app(self):
        with tempfile.TemporaryDirectory() as d:
            yield create_app(Path(d))

    def test_full_flow_config_and_ddl(self, runner, app):
        """Test config init + ddl add + ddl list flow."""
        # Config init
        r1 = runner.invoke(app, [
            "config", "init",
            "--base-url", "https://api.deepseek.com/v1",
            "--api-key", "sk-test-123",
            "--model", "deepseek-chat",
        ])
        assert r1.exit_code == 0

        # DDL add
        r2 = runner.invoke(app, [
            "ddl", "add", "测试系统",
            "--text", "CREATE TABLE users (id INT, name TEXT); CREATE TABLE orders (id INT, user_id INT);",
            "--tag", "测试",
        ])
        assert r2.exit_code == 0

        # DDL list
        r3 = runner.invoke(app, ["ddl", "list"])
        assert r3.exit_code == 0
        assert "测试系统" in r3.stdout
        assert "测试" in r3.stdout

        # DDL show
        r4 = runner.invoke(app, ["ddl", "show", "测试系统"])
        assert r4.exit_code == 0
        assert "CREATE TABLE users" in r4.stdout

        # Config show
        r5 = runner.invoke(app, ["config", "show"])
        assert r5.exit_code == 0
        assert "deepseek-chat" in r5.stdout
```

- [ ] **Step 2: Run integration test**

Run: `uv run pytest tests/test_integration.py -v`
Expected: All tests PASS

- [ ] **Step 3: Run all tests to verify nothing broken**

Run: `uv run pytest tests/ -v`
Expected: All tests across all modules PASS

- [ ] **Step 4: Final commit**

```bash
git add tests/test_integration.py
git commit -m "test: add integration smoke test"
```

---

## Self-Review Checklist

1. **Spec coverage:** Does every requirement from the spec have a corresponding task?
   - ✅ Config init/set/show — Task 3 (service), Task 4 (CLI)
   - ✅ DDL add (file + text) — Task 5 (store), Task 6 (service), Task 7 (CLI)
   - ✅ DDL list/show/delete — Task 5/6/7
   - ✅ DDL naming/tags — Task 5 (meta.json)
   - ✅ Chat start (with DB selection) — Task 8/9/10 (core), Task 11 (store), Task 12 (service), Task 13 (CLI)
   - ✅ Chat continue (with history) — Task 12 (get_latest_conversation), Task 13 (continue_ command)
   - ✅ Chat history — Task 11 (list_all), Task 13 (history command)
   - ✅ LLM config via config.toml — Task 3
   - ✅ OpenAI-compatible API — Task 8
   - ✅ Target DB: MySQL/PG/SQLite/MaxCompute — Task 12/13 (target_db parameter)
   - ✅ Multi-turn conversation — Task 12 (ask method saves history)

2. **Placeholder scan:** No TBD, TODO, or incomplete sections. All code is fully written.

3. **Type consistency:** All type annotations match across tasks. `LLMConfig`, `DDLMeta`, `Conversation`, `Message` are used consistently.

4. **Command names:** `my-tool config init/set/show`, `my-tool ddl add/list/show/delete`, `my-tool chat start/continue/history` — match the spec exactly.
