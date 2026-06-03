from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from my_tool.models import Conversation, Message


class ConversationStore:
    """File-based storage for conversation history.

    Each conversation is stored as:
        conversations/conv-<id>.json
    """

    def __init__(self, base_path: Path) -> None:
        self._base = base_path
        self._base.mkdir(parents=True, exist_ok=True)

    def _validate_name(self, conv_id: str) -> None:
        if not conv_id or conv_id.strip() != conv_id:
            raise ValueError(f"Invalid conversation ID: {conv_id!r}")
        if "/" in conv_id or "\\" in conv_id:
            raise ValueError(f"Conversation ID cannot contain path separators: {conv_id!r}")
        if conv_id in (".", ".."):
            raise ValueError(f"Conversation ID cannot be '.' or '..'")

    def save(self, conversation: Conversation) -> None:
        self._validate_name(conversation.id)
        conversation.updated_at = datetime.now(timezone.utc)
        self._base.mkdir(parents=True, exist_ok=True)
        file_path = self._base / f"{conversation.id}.json"
        file_path.write_text(
            conversation.model_dump_json(indent=2),
            encoding="utf-8",
        )

    def get(self, conv_id: str) -> Optional[Conversation]:
        self._validate_name(conv_id)
        file_path = self._base / f"{conv_id}.json"
        if not file_path.exists():
            return None
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None
        messages = [Message(**m) for m in data.get("messages", [])]
        return Conversation(**{**data, "messages": messages})

    def get_latest(self) -> Optional[Conversation]:
        if not self._base.exists():
            return None
        json_files = sorted(
            self._base.glob("*.json"),
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )
        if not json_files:
            return None
        return self.get(json_files[0].stem)

    def list_all(self) -> list[Conversation]:
        if not self._base.exists():
            return []
        convs = []
        for f in sorted(
            self._base.glob("*.json"),
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        ):
            conv = self.get(f.stem)
            if conv:
                convs.append(conv)
        return convs

    def exists(self, conv_id: str) -> bool:
        self._validate_name(conv_id)
        return (self._base / f"{conv_id}.json").exists()

    def delete(self, conv_id: str) -> None:
        self._validate_name(conv_id)
        file_path = self._base / f"{conv_id}.json"
        if not file_path.exists():
            raise FileNotFoundError(f"Conversation '{conv_id}' not found.")
        file_path.unlink()
