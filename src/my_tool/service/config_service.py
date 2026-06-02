from __future__ import annotations

from pathlib import Path

from my_tool.models import LLMConfig
from my_tool.storage.config_store import ConfigStore


class ConfigService:
    """Business logic for managing LLM configuration."""

    def __init__(self, base_path: Path) -> None:
        self._store = ConfigStore(base_path)

    def config_exists(self) -> bool:
        return self._store.load() is not None

    def get_config(self) -> LLMConfig:
        config = self._store.load()
        if config is None:
            raise FileNotFoundError(
                "Configuration not initialized. Run `my-tool config init` first."
            )
        return config

    def init_interactive(
        self,
        base_url: str,
        api_key: str,
        model: str = "gpt-4o",
    ) -> bool:
        config = LLMConfig(
            base_url=base_url,
            api_key=api_key,
            model=model,
        )
        self._store.save(config)
        return True

    def set(self, key: str, value: str) -> None:
        config = self.get_config()
        if not hasattr(config, key):
            raise ValueError(f"Unknown config key: {key}")
        setattr(config, key, value)
        self._store.save(config)

    def show(self) -> dict:
        config = self.get_config()
        return self._store.get_display_dict(config)
