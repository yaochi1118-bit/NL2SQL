"""Tests for the DDL REST API endpoints."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from fastapi.testclient import TestClient

from my_tool.api.server import create_app


def test_ddl_crud():
    """Test full DDL CRUD lifecycle via the REST API."""
    test_base = Path(__file__).resolve().parent / "test_data_ddl_api"

    try:
        if test_base.exists():
            shutil.rmtree(test_base)
        test_base.mkdir(parents=True)

        test_app = create_app(base_path=test_base)
        client = TestClient(test_app)

        # 1. List (empty)
        r = client.get("/api/ddls")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        assert r.json() == [], f"Expected empty list, got {r.json()}"

        # 2. Create
        r = client.post(
            "/api/ddls",
            json={"name": "test", "text": "CREATE TABLE users (id INT);", "tags": ["test"]},
        )
        assert r.status_code == 201, f"Expected 201, got {r.status_code}: {r.text}"
        assert r.json()["status"] == "ok"

        # 3. Get
        r = client.get("/api/ddls/test")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        data = r.json()
        assert data["name"] == "test"
        assert "CREATE TABLE users" in data["content"]
        assert data["meta"]["name"] == "test"

        # 4. List (has 1)
        r = client.get("/api/ddls")
        assert r.status_code == 200
        assert len(r.json()) == 1

        # 5. Delete
        r = client.delete("/api/ddls/test")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        assert r.json()["status"] == "deleted"

        # 6. List (empty again)
        r = client.get("/api/ddls")
        assert r.status_code == 200
        assert r.json() == []

        # 7. Get nonexistent -> 404
        r = client.get("/api/ddls/nonexistent")
        assert r.status_code == 404

        # 8. Delete nonexistent -> 404
        r = client.delete("/api/ddls/nonexistent")
        assert r.status_code == 404

        # 9. Duplicate create -> 409
        r = client.post("/api/ddls", json={"name": "dup", "text": "CREATE TABLE t (id INT);"})
        assert r.status_code == 201
        r = client.post("/api/ddls", json={"name": "dup", "text": "CREATE TABLE t2 (id INT);"})
        assert r.status_code == 409, f"Expected 409, got {r.status_code}: {r.text}"

        # 10. Force overwrite
        r = client.post(
            "/api/ddls", json={"name": "dup", "text": "CREATE TABLE t2 (id INT);", "force": True}
        )
        assert r.status_code == 201

        print("=== ALL DDL API TESTS PASSED ===")

    finally:
        if test_base.exists():
            shutil.rmtree(test_base)


if __name__ == "__main__":
    test_ddl_crud()
