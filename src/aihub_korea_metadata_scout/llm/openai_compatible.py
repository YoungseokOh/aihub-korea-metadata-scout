from __future__ import annotations

import json
from typing import Any

from aihub_korea_metadata_scout.llm.base import (
    IDEATION_SCHEMA,
    LLMConfigurationError,
    LLMProvider,
    LLMProviderError,
    extract_json_object,
)


class OpenAICompatibleProvider(LLMProvider):
    """Chat-completions backend for any OpenAI-compatible server.

    Covers LM Studio (local, default ``http://localhost:1234/v1``) and the hosted
    OpenAI / Codex API. The only differences are ``base_url``, ``api_key`` and the
    model id, so a single client implementation serves both.
    """

    def __init__(
        self,
        *,
        model: str,
        base_url: str | None,
        api_key: str | None,
        name: str = "openai-compatible",
    ) -> None:
        super().__init__(model=model)
        self.name = name
        self.base_url = base_url
        try:
            from openai import OpenAI
        except ImportError as error:  # pragma: no cover - depends on optional extra
            msg = (
                "The `openai` package is required for the LM Studio / OpenAI provider. "
                "Install it with `uv sync --extra llm` (or `pip install openai`)."
            )
            raise LLMConfigurationError(msg) from error

        # LM Studio ignores the key but the SDK still requires a non-empty value.
        self._client = OpenAI(base_url=base_url, api_key=api_key or "not-needed")

    def complete_json(self, *, system: str, user: str) -> dict[str, Any]:
        request: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.4,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "dataset_ideation",
                    "schema": IDEATION_SCHEMA,
                    "strict": True,
                },
            },
        }
        try:
            response = self._client.chat.completions.create(**request)
        except Exception:
            # Some local models reject json_schema; retry with plain json_object.
            request["response_format"] = {"type": "json_object"}
            try:
                response = self._client.chat.completions.create(**request)
            except Exception as retry_error:  # pragma: no cover - network/runtime dependent
                msg = f"OpenAI-compatible request failed: {retry_error}"
                raise LLMProviderError(msg) from retry_error

        content = response.choices[0].message.content if response.choices else None
        if not content:
            msg = "OpenAI-compatible response was empty."
            raise LLMProviderError(msg)

        try:
            return json.loads(content)
        except (TypeError, json.JSONDecodeError):
            return extract_json_object(content)
