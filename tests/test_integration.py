"""Smoke test — exercises the full flow: config init → ddl add → chat."""
import tempfile
from pathlib import Path

import pytest
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
