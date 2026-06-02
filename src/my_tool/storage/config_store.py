from __future__ import annotations

from pathlib import Path
from tomllib import TOMLDecodeError

import tomli_w

from my_tool.models import LLMConfig


class ConfigStore:
    """Read/write LLM configuration as config.toml."""

    FILENAME = "config.toml"

    def __init__(self, base_path: Path) -> None:
        self._path = base_path / self.FILENAME

    def save(self, config: LLMConfig) -> None:
        data = {
            "llm": {
                "provider": config.provider,
                "base_url": config.base_url,
                "api_key": config.api_key,
                "model": config.model,
            }
        }
        with open(self._path, "wb") as f:
            tomli_w.dump(data, f)

    def load(self) -> LLMConfig | None:
        if not self._path.exists():
            return None
        try:
            with open(self._path, "rb") as f:
                import tomllib

                data = tomllib.load(f)
            llm = data.get("llm", {})
            return LLMConfig(
                provider=llm.get("provider", "openai-compatible"),
                base_url=llm.get("base_url", ""),
                api_key=llm.get("api_key", ""),
                model=llm.get("model", "gpt-4o"),
            )
        except (TOMLDecodeError, KeyError, ValueError):
            return None

    def get_display_dict(self, config: LLMConfig) -> dict:
        """Return config dict with API key masked for safe display."""
        key = config.api_key
        masked = key[:5] + "***" + key[-3:] if len(key) > 8 else "***"
        return {
            "provider": config.provider,
            "base_url": config.base_url,
            "api_key": masked,
            "model": config.model,
        }
