from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from my_tool.core.llm_client import LLMClient
from my_tool.core.prompt_builder import PromptBuilder
from my_tool.core.sql_parser import SQLParser
from my_tool.models import Conversation, Message
from my_tool.service.config_service import ConfigService
from my_tool.service.ddl_service import DDLService
from my_tool.storage.conversation_store import ConversationStore


class ChatService:
    """Business logic for chat/SQL generation conversations."""

    def __init__(self, base_path: Path) -> None:
        self._config_service = ConfigService(base_path)
        self._ddl_service = DDLService(base_path)
        self._conv_store = ConversationStore(base_path / "conversations")

    def create_conversation(self, ddl_name: str, target_db: str) -> Conversation:
        """Create a new conversation for a given DDL."""
        if not self._ddl_service.exists(ddl_name):
            raise FileNotFoundError(f"DDL '{ddl_name}' not found.")

        conv_id = f"conv-{datetime.now().strftime('%Y%m%d')}-{ddl_name}-{uuid.uuid4().hex[:6]}"
        conv = Conversation(
            id=conv_id,
            ddl_name=ddl_name,
            target_db=target_db,
            messages=[],
        )
        self._conv_store.save(conv)
        return conv

    def ask(self, conv_id: str, question: str) -> dict:
        """Ask a question in an existing conversation.

        Returns:
            dict with keys: sql (str), raw_response (str), explanation (str),
                            valid (bool), messages (list[Message])
        """
        conv = self._conv_store.get(conv_id)
        if conv is None:
            raise FileNotFoundError(f"Conversation '{conv_id}' not found.")

        # Get DDL content
        ddl_result = self._ddl_service.get(conv.ddl_name)
        if ddl_result is None:
            raise FileNotFoundError(f"DDL '{conv.ddl_name}' not found.")
        ddl_content, _ = ddl_result

        # Build prompt
        system_prompt = PromptBuilder.build_system_prompt(ddl_content, conv.target_db)
        history = [{"role": m.role, "content": m.content} for m in conv.messages]
        messages = PromptBuilder.build_messages(system_prompt, history, question)

        # Call LLM
        config = self._config_service.get_config()
        client = LLMClient(config)
        response = client.chat(messages, stream=False)
        if isinstance(response, str):
            raw_response = response
        else:
            raw_response = "".join(list(response))

        # Parse SQL
        sql = SQLParser.extract_sql(raw_response)
        valid = SQLParser.validate_sql_basic(sql, conv.target_db)

        # Extract explanation (everything after the SQL block)
        explanation = raw_response
        if "```" in raw_response:
            parts = raw_response.split("```")
            if len(parts) > 2:
                explanation = parts[-1].strip() or ""

        # Save messages
        conv.messages.append(Message(role="user", content=question))
        conv.messages.append(Message(role="assistant", content=raw_response))
        self._conv_store.save(conv)

        return {
            "sql": sql if valid else "",
            "raw_response": raw_response,
            "explanation": explanation,
            "valid": valid,
            "messages": conv.messages,
        }

    def get_conversation(self, conv_id: str) -> Optional[Conversation]:
        return self._conv_store.get(conv_id)

    def get_latest_conversation(self) -> Optional[Conversation]:
        return self._conv_store.get_latest()

    def list_conversations(self) -> list[Conversation]:
        return self._conv_store.list_all()
