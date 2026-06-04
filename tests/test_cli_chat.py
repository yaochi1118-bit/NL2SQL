import tempfile
from pathlib import Path

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
        result = runner.invoke(
            app, ["start", "电商系统", "--target-db", "PostgreSQL"],
            input="q\n",
        )
        assert result.exit_code == 0
        assert "started" in result.stdout.lower()

    def test_chat_start_nonexistent_ddl(self, runner, app):
        result = runner.invoke(app, ["start", "不存在", "--target-db", "MySQL"])
        assert result.exit_code != 0

    def test_chat_history_empty(self, runner, app):
        result = runner.invoke(app, ["history"])
        assert result.exit_code == 0
