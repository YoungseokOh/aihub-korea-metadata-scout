from __future__ import annotations

from aihub_korea_metadata_scout.config import ScoutSettings
from aihub_korea_metadata_scout.llm.base import LLMConfigurationError, LLMProvider

# Sensible defaults per provider so a bare `ideate` works out of the box for the
# common local setup (LM Studio) while staying overridable via env vars / flags.
LMSTUDIO_DEFAULT_BASE_URL = "http://localhost:1234/v1"
LMSTUDIO_DEFAULT_MODEL = "local-model"
OPENAI_DEFAULT_MODEL = "gpt-4o-mini"

_PROVIDER_ALIASES = {
    "lmstudio": "lmstudio",
    "lm-studio": "lmstudio",
    "lm_studio": "lmstudio",
    "local": "lmstudio",
    "openai": "openai",
    "codex": "openai",
    "anthropic": "anthropic",
    "claude": "anthropic",
}


def resolve_provider_name(raw: str | None) -> str:
    key = (raw or "lmstudio").strip().casefold()
    if key not in _PROVIDER_ALIASES:
        supported = ", ".join(sorted(set(_PROVIDER_ALIASES.values())))
        msg = f"Unknown LLM provider `{raw}`. Supported providers: {supported}."
        raise LLMConfigurationError(msg)
    return _PROVIDER_ALIASES[key]


def build_provider(
    settings: ScoutSettings,
    *,
    provider: str | None = None,
    model: str | None = None,
) -> LLMProvider:
    """Construct the configured LLM provider.

    Resolution order for each field: explicit argument -> settings/env -> default.
    """

    name = resolve_provider_name(provider or settings.llm_provider)
    chosen_model = model or settings.llm_model

    if name == "anthropic":
        from aihub_korea_metadata_scout.llm.anthropic_provider import (
            DEFAULT_ANTHROPIC_MODEL,
            AnthropicProvider,
        )

        return AnthropicProvider(
            model=chosen_model or DEFAULT_ANTHROPIC_MODEL,
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
        )

    from aihub_korea_metadata_scout.llm.openai_compatible import OpenAICompatibleProvider

    if name == "lmstudio":
        return OpenAICompatibleProvider(
            model=chosen_model or LMSTUDIO_DEFAULT_MODEL,
            base_url=settings.llm_base_url or LMSTUDIO_DEFAULT_BASE_URL,
            api_key=settings.llm_api_key,
            name="lmstudio",
        )

    # name == "openai" / "codex"
    return OpenAICompatibleProvider(
        model=chosen_model or OPENAI_DEFAULT_MODEL,
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        name="openai",
    )
