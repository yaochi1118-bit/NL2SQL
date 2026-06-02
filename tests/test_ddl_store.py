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
