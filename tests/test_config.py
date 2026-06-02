import json
import os
import tempfile
from pathlib import Path

import pytest
from pydantic import ValidationError

from my_tool.models import LLMConfig
from my_tool.storage.config_store import ConfigStore
from my_tool.service.config_service import ConfigService


class TestConfigStore:
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as d:
            yield Path(d)

    def test_save_and_load_config(self, temp_dir):
        store = ConfigStore(temp_dir)
        config = LLMConfig(
            base_url="https://api.deepseek.com/v1",
            api_key="sk-test-key",
            model="deepseek-chat",
        )
        store.save(config)
        loaded = store.load()
        assert loaded.base_url == "https://api.deepseek.com/v1"
        assert loaded.api_key == "sk-test-key"
        assert loaded.model == "deepseek-chat"
        assert loaded.provider == "openai-compatible"

    def test_load_missing_config(self, temp_dir):
        store = ConfigStore(temp_dir)
        assert store.load() is None

    def test_api_key_masked_in_display(self, temp_dir):
        store = ConfigStore(temp_dir)
        config = LLMConfig(
            base_url="https://api.openai.com/v1",
            api_key="sk-abcdefghijklmnop",
        )
        display = store.get_display_dict(config)
        assert "sk-ab***nop" in display["api_key"]
        assert "sk-abcdefghijklmnop" not in display["api_key"]


class TestConfigService:
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as d:
            yield Path(d)

    def test_init_interactive_creates_config(self, temp_dir):
        service = ConfigService(temp_dir)
        result = service.init_interactive(
            base_url="https://api.deepseek.com/v1",
            api_key="sk-test",
            model="deepseek-chat",
        )
        assert result is True
        loaded = service.get_config()
        assert loaded.base_url == "https://api.deepseek.com/v1"
        assert loaded.api_key == "sk-test"

    def test_set_config_value(self, temp_dir):
        service = ConfigService(temp_dir)
        service.init_interactive(
            base_url="https://api.openai.com/v1",
            api_key="sk-test",
            model="gpt-4o",
        )
        service.set("model", "gpt-4o-mini")
        loaded = service.get_config()
        assert loaded.model == "gpt-4o-mini"

    def test_get_config_before_init_raises(self, temp_dir):
        service = ConfigService(temp_dir)
        with pytest.raises(FileNotFoundError, match="not initialized"):
            service.get_config()

    def test_config_exists_check(self, temp_dir):
        service = ConfigService(temp_dir)
        assert service.config_exists() is False
        service.init_interactive(
            base_url="https://api.openai.com/v1",
            api_key="sk-test",
        )
        assert service.config_exists() is True
