import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from my_tool.service.chat_service import ChatService
from my_tool.service.config_service import ConfigService
from my_tool.service.ddl_service import DDLService


class TestChatService:
    @pytest.fixture
    def chat_service(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            # Initialize config
            ConfigService(base).init_interactive(
                base_url="https://api.openai.com/v1",
                api_key="sk-test",
            )
            # Add a DDL
            DDLService(base).add("电商系统", "CREATE TABLE users (id INT);")
            yield ChatService(base)

    def test_create_conversation(self, chat_service):
        conv = chat_service.create_conversation("电商系统", "PostgreSQL")
        assert conv.ddl_name == "电商系统"
        assert conv.target_db == "PostgreSQL"
        assert conv.id.startswith("conv-")

    def test_create_conversation_nonexistent_ddl(self, chat_service):
        with pytest.raises(FileNotFoundError):
            chat_service.create_conversation("不存在的系统", "MySQL")

    @patch("my_tool.core.llm_client.LLMClient.chat")
    def test_ask_question(self, mock_chat, chat_service):
        mock_chat.return_value = "```sql\nSELECT * FROM users;\n```"
        conv = chat_service.create_conversation("电商系统", "PostgreSQL")
        result = chat_service.ask(conv.id, "查询所有用户")

        assert result["sql"] == "SELECT * FROM users;"
        assert len(result["messages"]) == 2  # user + assistant

    @patch("my_tool.core.llm_client.LLMClient.chat")
    def test_ask_invalid_sql_response(self, mock_chat, chat_service):
        mock_chat.return_value = "I don't know how to answer that."
        conv = chat_service.create_conversation("电商系统", "PostgreSQL")
        result = chat_service.ask(conv.id, "查询所有用户")

        assert result["valid"] is False
        assert result["sql"] == ""

    def test_ask_in_nonexistent_conversation(self, chat_service):
        with pytest.raises(FileNotFoundError):
            chat_service.ask("conv-nonexistent", "test")

    def test_ask_without_init(self, chat_service):
        conv = chat_service.create_conversation("电商系统", "PostgreSQL")
        chat_service._config_service = ConfigService(Path("/nonexistent"))
        with pytest.raises(FileNotFoundError):
            chat_service.ask(conv.id, "test")

    def test_get_conversation(self, chat_service):
        conv = chat_service.create_conversation("电商系统", "MySQL")
        loaded = chat_service.get_conversation(conv.id)
        assert loaded is not None
        assert loaded.id == conv.id

    def test_list_conversations(self, chat_service):
        chat_service.create_conversation("电商系统", "PG")
        chat_service.create_conversation("电商系统", "MySQL")
        convs = chat_service.list_conversations()
        assert len(convs) == 2
