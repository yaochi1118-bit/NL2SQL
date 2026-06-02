import tempfile
from pathlib import Path

import pytest
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
            "--model", "deepseek-chat",
        ])
        result = runner.invoke(app, ["show"])
        assert result.exit_code == 0
        assert "sk-te***123" in result.stdout

    def test_config_set(self, runner, temp_dir):
        app = get_config_app(temp_dir)
        runner.invoke(app, [
            "init", "--base-url", "https://api.openai.com/v1",
            "--api-key", "sk-test",
            "--model", "gpt-4o",
        ])
        result = runner.invoke(app, ["set", "model", "gpt-4o-mini"])
        assert result.exit_code == 0
        assert "model" in result.stdout.lower()

    def test_config_show_before_init(self, runner, temp_dir):
        app = get_config_app(temp_dir)
        result = runner.invoke(app, ["show"])
        assert result.exit_code != 0
