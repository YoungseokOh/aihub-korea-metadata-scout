from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from typing import Any


class LLMProviderError(RuntimeError):
    """Raised when an LLM backend call fails or returns unusable output."""


class LLMConfigurationError(LLMProviderError):
    """Raised when an LLM backend is misconfigured (missing dep, url, key, ...)."""


# JSON schema for the ideation payload the model must return. Kept intentionally
# flat (no recursion, no numeric constraints beyond enums) so it works across
# Anthropic structured outputs and OpenAI-compatible json_schema response formats.
IDEATION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "overall_verdict": {"type": "string"},
        "notes": {"type": "array", "items": {"type": "string"}},
        "ideas": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "name": {"type": "string"},
                    "one_liner": {"type": "string"},
                    "app_or_web": {"type": "string", "enum": ["app", "web", "both"]},
                    "target_users": {"type": "array", "items": {"type": "string"}},
                    "core_features": {"type": "array", "items": {"type": "string"}},
                    "data_usage": {"type": "string"},
                    "feasibility": {"type": "string", "enum": ["go", "maybe", "no-go"]},
                    "opportunity_score": {"type": "integer"},
                    "feasibility_score": {"type": "integer"},
                    "data_fit_score": {"type": "integer"},
                    "risks": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "name",
                    "one_liner",
                    "app_or_web",
                    "target_users",
                    "core_features",
                    "data_usage",
                    "feasibility",
                    "opportunity_score",
                    "feasibility_score",
                    "data_fit_score",
                    "risks",
                ],
            },
        },
    },
    "required": ["overall_verdict", "notes", "ideas"],
}

_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE)


def extract_json_object(text: str) -> dict[str, Any]:
    """Parse a JSON object from raw model text, tolerating code fences and prose.

    Local models (LM Studio) do not always honour structured-output requests, so
    we defend against ```json fences and leading/trailing commentary.
    """

    candidate = text.strip()
    if candidate.startswith("```"):
        candidate = _FENCE_RE.sub("", candidate).strip()

    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass

    start = candidate.find("{")
    end = candidate.rfind("}")
    if start != -1 and end != -1 and end > start:
        snippet = candidate[start : end + 1]
        try:
            return json.loads(snippet)
        except json.JSONDecodeError as error:
            msg = f"Model did not return valid JSON: {error}"
            raise LLMProviderError(msg) from error

    msg = "Model response did not contain a JSON object."
    raise LLMProviderError(msg)


class LLMProvider(ABC):
    """Common interface for every LLM backend used for ideation."""

    #: Stable identifier stored in artifacts (e.g. "lmstudio", "openai", "anthropic").
    name: str = "llm"

    def __init__(self, *, model: str) -> None:
        self.model = model

    @abstractmethod
    def complete_json(self, *, system: str, user: str) -> dict[str, Any]:
        """Return a JSON object matching ``IDEATION_SCHEMA`` for the given prompt."""
