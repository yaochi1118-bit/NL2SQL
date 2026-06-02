from datetime import datetime

import pytest
from pydantic import ValidationError

from my_tool.models import LLMConfig, DDLMeta, Conversation, Message


def test_llm_config_defaults():
    config = LLMConfig(api_key="sk-test", base_url="https://api.openai.com/v1")
    assert config.provider == "openai-compatible"
    assert config.model == "gpt-4o"
    assert config.api_key == "sk-test"


def test_llm_config_no_api_key():
    with pytest.raises(ValidationError):
        LLMConfig(api_key="", base_url="https://api.openai.com/v1")


def test_ddl_meta_with_tags():
    meta = DDLMeta(name="电商系统", tags=["生产"])
    assert meta.name == "电商系统"
    assert "生产" in meta.tags
    assert meta.table_count == 0


def test_ddl_meta_defaults():
    meta = DDLMeta(name="测试系统")
    assert meta.tags == []
    assert meta.table_count == 0


def test_conversation_create():
    conv = Conversation(
        id="conv-test-1",
        ddl_name="电商系统",
        target_db="PostgreSQL",
        messages=[Message(role="user", content="test")]
    )
    assert conv.message_count == 1
    assert conv.messages[0].role == "user"


def test_conversation_default_updated_at():
    conv = Conversation(
        id="conv-test-2",
        ddl_name="电商系统",
        target_db="MySQL",
        messages=[]
    )
    assert isinstance(conv.created_at, datetime)
    assert isinstance(conv.updated_at, datetime)


def test_message_create():
    msg = Message(role="assistant", content="SELECT * FROM users;")
    assert msg.role == "assistant"
    assert msg.content == "SELECT * FROM users;"
