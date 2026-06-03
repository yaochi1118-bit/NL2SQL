import tempfile
from pathlib import Path

import pytest

from my_tool.models import Conversation, Message
from my_tool.storage.conversation_store import ConversationStore


class TestConversationStore:
    @pytest.fixture
    def store(self):
        with tempfile.TemporaryDirectory() as d:
            yield ConversationStore(Path(d) / "conversations")

    def test_save_and_get_conversation(self, store):
        conv = Conversation(
            id="conv-test-1",
            ddl_name="电商系统",
            target_db="PostgreSQL",
            messages=[Message(role="user", content="test")],
        )
        store.save(conv)
        loaded = store.get("conv-test-1")
        assert loaded is not None
        assert loaded.id == "conv-test-1"
        assert loaded.ddl_name == "电商系统"
        assert loaded.message_count == 1

    def test_get_latest(self, store):
        conv1 = Conversation(id="conv-old", ddl_name="A", target_db="MySQL", messages=[])
        conv2 = Conversation(id="conv-new", ddl_name="B", target_db="PG", messages=[])
        store.save(conv1)
        store.save(conv2)
        latest = store.get_latest()
        assert latest is not None
        assert latest.id == "conv-new"

    def test_get_latest_empty(self, store):
        assert store.get_latest() is None

    def test_list_all(self, store):
        store.save(Conversation(id="c1", ddl_name="A", target_db="M", messages=[]))
        store.save(Conversation(id="c2", ddl_name="B", target_db="P", messages=[]))
        conv_list = store.list_all()
        assert len(conv_list) == 2

    def test_delete(self, store):
        store.save(Conversation(id="c-del", ddl_name="X", target_db="Y", messages=[]))
        store.delete("c-del")
        assert store.get("c-del") is None

    def test_update_existing(self, store):
        conv = Conversation(id="c-upd", ddl_name="S", target_db="SQLite", messages=[])
        store.save(conv)
        conv.messages.append(Message(role="user", content="new msg"))
        store.save(conv)
        loaded = store.get("c-upd")
        assert loaded is not None
        assert loaded.message_count == 1

    def test_get_nonexistent_returns_none(self, store):
        assert store.get("nonexistent") is None

    def test_list_all_empty(self, store):
        assert store.list_all() == []
