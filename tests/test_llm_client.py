from unittest.mock import MagicMock, patch

import pytest
from openai import APIError

from my_tool.core.llm_client import LLMClient
from my_tool.models import LLMConfig


class TestLLMClient:
    @pytest.fixture
    def config(self):
        return LLMConfig(
            base_url="https://api.openai.com/v1",
            api_key="sk-test",
            model="gpt-4o",
        )

    @patch("my_tool.core.llm_client.OpenAI")
    def test_client_initialization(self, mock_openai, config):
        client = LLMClient(config)
        assert client.model == "gpt-4o"
        mock_openai.assert_called_once_with(
            base_url="https://api.openai.com/v1",
            api_key="sk-test",
        )

    @patch("my_tool.core.llm_client.OpenAI")
    def test_chat_success(self, mock_openai, config):
        mock_instance = MagicMock()
        mock_openai.return_value = mock_instance
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "SELECT * FROM users;"
        mock_instance.chat.completions.create.return_value = mock_response

        client = LLMClient(config)
        result = client.chat([{"role": "user", "content": "test"}], stream=False)

        assert result == "SELECT * FROM users;"
        mock_instance.chat.completions.create.assert_called_once()

    @patch("my_tool.core.llm_client.OpenAI")
    def test_chat_stream(self, mock_openai, config):
        mock_instance = MagicMock()
        mock_openai.return_value = mock_instance

        # Simulate streaming chunks
        chunk1 = MagicMock()
        chunk1.choices[0].delta.content = "SELECT"
        chunk2 = MagicMock()
        chunk2.choices[0].delta.content = " * FROM"
        chunk3 = MagicMock()
        chunk3.choices[0].delta.content = " users;"

        mock_stream = MagicMock()
        mock_stream.__iter__.return_value = [chunk1, chunk2, chunk3]
        mock_instance.chat.completions.create.return_value = mock_stream

        client = LLMClient(config)
        collected = []
        for chunk in client.chat([{"role": "user", "content": "test"}], stream=True):
            collected.append(chunk)

        full = "".join(collected)
        assert "SELECT * FROM users;" in full

    @patch("my_tool.core.llm_client.OpenAI")
    def test_chat_api_error(self, mock_openai, config):
        mock_instance = MagicMock()
        mock_openai.return_value = mock_instance
        mock_instance.chat.completions.create.side_effect = APIError(
            message="Test error",
            request=MagicMock(),
            body=None,
        )

        client = LLMClient(config)
        with pytest.raises(APIError):
            client.chat([{"role": "user", "content": "test"}], stream=False)
