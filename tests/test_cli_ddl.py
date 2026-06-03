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
