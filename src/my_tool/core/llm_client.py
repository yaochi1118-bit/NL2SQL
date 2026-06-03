from __future__ import annotations

from collections.abc import Generator

from openai import OpenAI

from my_tool.models import LLMConfig


class LLMClient:
    """OpenAI-compatible API client for LLM interactions."""

    def __init__(self, config: LLMConfig) -> None:
        self._client = OpenAI(
            base_url=config.base_url,
            api_key=config.api_key,
        )
        self.model = config.model

    def chat(
        self,
        messages: list[dict],
        stream: bool = True,
        **kwargs,
    ) -> str | Generator[str, None, None]:
        """Send a chat completion request.

        Additional keyword arguments are forwarded to
        ``openai.OpenAI.chat.completions.create()`` (e.g. temperature, max_tokens).

        If stream=False, returns the full response string. API errors are raised
        immediately at the call site.

        If stream=True, returns a generator yielding content chunks. **API errors
        are raised lazily** — they surface when the generator is first iterated,
        not at the ``chat()`` call site.

        Args:
            messages: List of message dicts with ``role`` and ``content`` keys.
            stream: Whether to stream the response.
            **kwargs: Additional parameters forwarded to the API (e.g.
                temperature=0.2, max_tokens=500).
        """
        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=stream,
            **kwargs,
        )

        if stream:

            def generate() -> Generator[str, None, None]:
                for chunk in response:
                    delta = chunk.choices[0].delta if chunk.choices else None
                    if delta and delta.content:
                        yield delta.content

            return generate()
        else:
            return response.choices[0].message.content if response.choices else ""
