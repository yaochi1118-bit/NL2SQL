"""Tests for the Chat and Config REST API endpoints."""

from __future__ import annotations

import shutil
from pathlib import Path

from fastapi.testclient import TestClient

from my_tool.api.server import create_app


def test_config_and_chat_api():
    """Test config and chat API lifecycle."""
    test_base = Path(__file__).resolve().parent / "test_data_chat_config_api"

    try:
        if test_base.exists():
            shutil.rmtree(test_base)
        test_base.mkdir(parents=True)

        test_app = create_app(base_path=test_base)
        client = TestClient(test_app)

        # 1. Config status (no config yet)
        r = client.get("/api/config/status")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        assert r.json() == {"exists": False}

        # 2. Config init
        r = client.post(
            "/api/config/init",
            json={
                "base_url": "https://api.openai.com/v1",
                "api_key": "sk-test1234567890",
                "model": "gpt-4o",
            },
        )
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        assert r.json() == {"status": "ok"}

        # 3. Config get (masked API key)
        r = client.get("/api/config")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        data = r.json()
        assert data["api_key"] == "sk-te***890", f"Unexpected masked key: {data['api_key']}"
        assert data["base_url"] == "https://api.openai.com/v1"
        assert data["model"] == "gpt-4o"

        # 4. Config status (now exists)
        r = client.get("/api/config/status")
        assert r.status_code == 200
        assert r.json() == {"exists": True}

        # 5. Config update
        r = client.put("/api/config", json={"key": "model", "value": "gpt-4-turbo"})
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        assert r.json() == {"status": "ok"}

        # Verify the update
        r = client.get("/api/config")
        assert r.status_code == 200
        assert r.json()["model"] == "gpt-4-turbo"

        # 6. Conversations list empty
        r = client.get("/api/conversations")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        assert r.json() == [], f"Expected empty list, got {r.json()}"

        # 7. Create conversation (requires a DDL first)
        r = client.post(
            "/api/ddls",
            json={
                "name": "test_table",
                "text": "CREATE TABLE users (id INT);",
                "tags": ["test"],
            },
        )
        assert r.status_code == 201

        r = client.post(
            "/api/conversations",
            json={"ddl_name": "test_table", "target_db": "postgresql"},
        )
        assert r.status_code == 201, f"Expected 201, got {r.status_code}: {r.text}"
        conv_data = r.json()
        assert conv_data["ddl_name"] == "test_table"
        assert conv_data["target_db"] == "postgresql"
        assert "id" in conv_data

        conv_id = conv_data["id"]

        # 8. Get conversation
        r = client.get(f"/api/conversations/{conv_id}")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        assert r.json()["id"] == conv_id

        # 9. List conversations (has 1)
        r = client.get("/api/conversations")
        assert r.status_code == 200
        assert len(r.json()) == 1

        # 10. Delete nonexistent conversation -> 404
        r = client.delete("/api/conversations/nonexistent")
        assert r.status_code == 404, f"Expected 404, got {r.status_code}: {r.text}"

        # 11. Delete existing conversation
        r = client.delete(f"/api/conversations/{conv_id}")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        assert r.json()["status"] == "deleted"

        # 12. List conversations (empty again)
        r = client.get("/api/conversations")
        assert r.status_code == 200
        assert r.json() == []

        print("=== ALL CHAT & CONFIG API TESTS PASSED ===")

    finally:
        if test_base.exists():
            shutil.rmtree(test_base)


if __name__ == "__main__":
    test_config_and_chat_api()
