import tempfile
from pathlib import Path

import pytest
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
