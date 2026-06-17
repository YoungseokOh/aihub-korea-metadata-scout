from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from aihub_korea_metadata_scout.config import ScoutSettings
from aihub_korea_metadata_scout.llm.base import LLMProvider
from aihub_korea_metadata_scout.llm.prompts import SYSTEM_PROMPT, build_user_prompt
from aihub_korea_metadata_scout.models import (
    DatasetSummary,
    IdeationResult,
    ProductIdea,
    path_to_str,
)
from aihub_korea_metadata_scout.storage.json_store import (
    dataset_summary_path,
    ideation_result_path,
    write_ideation_result,
)
from aihub_korea_metadata_scout.storage.markdown_store import (
    ideation_markdown_path,
    write_markdown,
)

TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "templates"


def _environment() -> Environment:
    return Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(default_for_string=False),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _clamp(value: object, default: int = 5) -> int:
    try:
        number = int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default
    return max(1, min(10, number))


def _coerce_idea(raw: dict) -> ProductIdea:
    surface = str(raw.get("app_or_web", "both")).strip().casefold()
    if surface not in {"app", "web", "both"}:
        surface = "both"
    feasibility = str(raw.get("feasibility", "maybe")).strip().casefold()
    if feasibility not in {"go", "maybe", "no-go"}:
        feasibility = "maybe"
    return ProductIdea(
        name=str(raw.get("name", "")).strip() or "이름 미정 아이디어",
        one_liner=str(raw.get("one_liner", "")).strip(),
        app_or_web=surface,  # type: ignore[arg-type]
        target_users=[str(item) for item in raw.get("target_users", []) if str(item).strip()],
        core_features=[str(item) for item in raw.get("core_features", []) if str(item).strip()],
        data_usage=str(raw.get("data_usage", "")).strip(),
        feasibility=feasibility,  # type: ignore[arg-type]
        opportunity_score=_clamp(raw.get("opportunity_score")),
        feasibility_score=_clamp(raw.get("feasibility_score")),
        data_fit_score=_clamp(raw.get("data_fit_score")),
        risks=[str(item) for item in raw.get("risks", []) if str(item).strip()],
    )


def parse_ideation_payload(
    summary: DatasetSummary,
    payload: dict,
    *,
    provider: str,
    model: str,
    max_ideas: int,
) -> IdeationResult:
    raw_ideas = payload.get("ideas", [])
    ideas = [_coerce_idea(item) for item in raw_ideas if isinstance(item, dict)][:max_ideas]
    notes = [str(item) for item in payload.get("notes", []) if str(item).strip()]
    return IdeationResult(
        dataset_key=summary.dataset_key,
        title=summary.title,
        provider=provider,
        model=model,
        generated_at=datetime.now(UTC),
        overall_verdict=str(payload.get("overall_verdict", "")).strip(),
        notes=notes,
        ideas=ideas,
    )


def render_ideation_markdown(result: IdeationResult) -> str:
    template = _environment().get_template("dataset_ideation.md.j2")
    return template.render(result=result)


def generate_ideation_markdown(settings: ScoutSettings, result: IdeationResult) -> Path:
    settings.ensure_directories()
    body = render_ideation_markdown(result)
    markdown_path = ideation_markdown_path(settings, result)
    write_markdown(markdown_path, body)
    result.markdown_output_path = path_to_str(markdown_path)
    return markdown_path


def ideate_dataset(
    settings: ScoutSettings,
    summary: DatasetSummary,
    provider: LLMProvider,
    *,
    max_ideas: int = 5,
) -> IdeationResult:
    """Run metadata-only LLM ideation for one dataset and persist artifacts."""

    settings.ensure_directories()
    system = SYSTEM_PROMPT
    user = build_user_prompt(summary, max_ideas=max_ideas)
    payload = provider.complete_json(system=system, user=user)

    result = parse_ideation_payload(
        summary,
        payload,
        provider=provider.name,
        model=provider.model,
        max_ideas=max_ideas,
    )
    result.source_summary_path = path_to_str(dataset_summary_path(settings, summary.dataset_key))

    normalized_path = ideation_result_path(settings, summary.dataset_key)
    result.normalized_output_path = path_to_str(normalized_path)
    markdown_path = generate_ideation_markdown(settings, result)
    result.markdown_output_path = path_to_str(markdown_path)
    write_ideation_result(settings, result)
    return result


def ideation_debug_payload(summary: DatasetSummary, *, max_ideas: int = 5) -> str:
    """Return the exact user prompt for inspection/debugging (no LLM call)."""

    return json.dumps(
        {"system": SYSTEM_PROMPT, "user": build_user_prompt(summary, max_ideas=max_ideas)},
        ensure_ascii=False,
        indent=2,
    )
