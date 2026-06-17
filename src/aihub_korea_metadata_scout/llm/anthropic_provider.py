from __future__ import annotations

from typing import Any

from aihub_korea_metadata_scout.llm.base import (
    IDEATION_SCHEMA,
    LLMConfigurationError,
    LLMProvider,
    LLMProviderError,
    extract_json_object,
)

# Default to the latest, most capable Claude model. Override via AIHUB_LLM_MODEL.
DEFAULT_ANTHROPIC_MODEL = "claude-opus-4-8"


class AnthropicProvider(LLMProvider):
    """Claude backend using the official Anthropic SDK and structured outputs."""

    def __init__(
        self,
        *,
        model: str = DEFAULT_ANTHROPIC_MODEL,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        super().__init__(model=model)
        self.name = "anthropic"
        try:
            import anthropic
        except ImportError as error:  # pragma: no cover - depends on optional extra
            msg = (
                "The `anthropic` package is required for the Claude provider. "
                "Install it with `uv sync --extra llm` (or `pip install anthropic`)."
            )
            raise LLMConfigurationError(msg) from error

        client_kwargs: dict[str, Any] = {}
        if api_key:
            client_kwargs["api_key"] = api_key
        if base_url:
            client_kwargs["base_url"] = base_url
        try:
            self._client = anthropic.Anthropic(**client_kwargs)
        except Exception as error:  # pragma: no cover - misconfig (e.g. missing key)
            msg = f"Could not initialize the Anthropic client: {error}"
            raise LLMConfigurationError(msg) from error

    def complete_json(self, *, system: str, user: str) -> dict[str, Any]:
        try:
            response = self._client.messages.create(
                model=self.model,
                max_tokens=16000,
                system=system,
                thinking={"type": "adaptive"},
                output_config={
                    "format": {
                        "type": "json_schema",
                        "schema": IDEATION_SCHEMA,
                    }
                },
                messages=[{"role": "user", "content": user}],
            )
        except Exception as error:  # pragma: no cover - network/runtime dependent
            msg = f"Anthropic request failed: {error}"
            raise LLMProviderError(msg) from error

        text = next(
            (block.text for block in response.content if getattr(block, "type", None) == "text"),
            None,
        )
        if not text:
            msg = "Anthropic response did not contain a text block."
            raise LLMProviderError(msg)
        return extract_json_object(text)
