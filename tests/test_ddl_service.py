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
