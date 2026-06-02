from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    """LLM provider configuration (OpenAI-compatible API)."""

    provider: str = "openai-compatible"
    base_url: str
    api_key: str = Field(min_length=1)
    model: str = "gpt-4o"


class DDLMeta(BaseModel):
    """Metadata for an uploaded DDL schema."""

    name: str
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    table_count: int = 0


class Message(BaseModel):
    """A single message in a conversation."""

    role: str  # "system" | "user" | "assistant"
    content: str


class Conversation(BaseModel):
    """A chat conversation with history."""

    id: str
    ddl_name: str
    target_db: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    messages: list[Message] = Field(default_factory=list)

    @property
    def message_count(self) -> int:
        return len(self.messages)
