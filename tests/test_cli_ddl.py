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
        r1 = runner.invoke(app, ["add", "系统A", "--text", "DDL A"])
        assert r1.exit_code == 0
        r2 = runner.invoke(app, ["add", "系统B", "--text", "DDL B"])
        assert r2.exit_code == 0
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "系统A" in result.stdout
        assert "系统B" in result.stdout

    def test_ddl_show(self, runner, app):
        runner.invoke(app, ["add", "测试系统", "--text", "CREATE TABLE t (id INT);"])
        result = runner.invoke(app, ["show", "测试系统"])
        assert result.exit_code == 0
        assert "CREATE TABLE t" in result.stdout

    def test_ddl_add_both_file_and_text(self, runner, app):
        result = runner.invoke(app, [
            "add", "系统", "--file", "a.sql", "--text", "DDL",
        ])
        assert result.exit_code != 0
        assert "cannot use both" in result.stdout.lower()

    def test_ddl_add_neither_file_nor_text(self, runner, app):
        result = runner.invoke(app, ["add", "系统"])
        assert result.exit_code != 0
        assert "provide" in result.stdout.lower()

    def test_ddl_add_from_file(self, runner, app):
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".sql", mode="w", delete=False) as f:
            f.write("CREATE TABLE test (id INT);")
            f.flush()
            result = runner.invoke(app, [
                "add", "文件导入", "--file", f.name,
            ])
        assert result.exit_code == 0
        assert "saved" in result.stdout.lower()
        # Verify it's listed
        list_result = runner.invoke(app, ["list"])
        assert "文件导入" in list_result.stdout

    def test_ddl_list_empty(self, runner, app):
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "no ddl" in result.stdout.lower()

    def test_ddl_show_nonexistent(self, runner, app):
        result = runner.invoke(app, ["show", "不存在的系统"])
        assert result.exit_code != 0
        assert "not found" in result.stdout.lower()

    def test_ddl_delete_nonexistent(self, runner, app):
        result = runner.invoke(app, ["delete", "不存在的系统"])
        assert result.exit_code != 0
        assert "not found" in result.stdout.lower()

    def test_ddl_delete(self, runner, app):
        runner.invoke(app, ["add", "待删除", "--text", "DDL"])
        result = runner.invoke(app, ["delete", "待删除"])
        assert result.exit_code == 0
        assert "deleted" in result.stdout.lower()
        # Verify it's actually gone
        list_result = runner.invoke(app, ["list"])
        assert "待删除" not in list_result.stdout
