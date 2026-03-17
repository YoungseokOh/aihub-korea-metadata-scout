from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from aihub_korea_metadata_scout.config import ScoutSettings
from aihub_korea_metadata_scout.models import DatasetSummary
from aihub_korea_metadata_scout.storage.json_store import load_dataset_summaries, write_json
from aihub_korea_metadata_scout.storage.markdown_store import catalog_markdown_path, write_markdown


def _section_items(
    summaries: list[DatasetSummary],
    *,
    key_name: str,
    reverse: bool = True,
    limit: int = 10,
) -> list[DatasetSummary]:
    return sorted(
        summaries,
        key=lambda item: getattr(item, key_name) or 0,
        reverse=reverse,
    )[:limit]


def _filter_multimodal(summaries: list[DatasetSummary]) -> list[DatasetSummary]:
    return [
        item for item in summaries if item.modality_guess and "multimodal" in item.modality_guess
    ]


def _filter_b2b(summaries: list[DatasetSummary]) -> list[DatasetSummary]:
    needles = ("공공기관", "엔터프라이즈", "운영팀", "병원", "플랫폼", "스타트업", "기관")
    return [
        item
        for item in summaries
        if any(any(needle in segment for needle in needles) for segment in item.customer_segments)
    ]


def _filter_consumer(summaries: list[DatasetSummary]) -> list[DatasetSummary]:
    needles = ("교육", "consumer", "학습", "반려견", "에듀테크")
    return [
        item
        for item in summaries
        if any(
            any(needle.casefold() in segment.casefold() for needle in needles)
            for segment in item.customer_segments
        )
    ]


def _entry_line(summary: DatasetSummary) -> str:
    return (
        f"- `{summary.dataset_key}` {summary.title} | 기회 {summary.opportunity_score}/10 | "
        f"난이도 {summary.difficulty_score}/10 | 준비도 {summary.data_readiness_score}/10 | "
        f"{summary.inferred_summary}"
    )


def _render_markdown(sections: dict[str, list[DatasetSummary]], generated_at: datetime) -> str:
    lines = [
        "# AI-Hub Korea Metadata Catalog",
        "",
        f"생성 시각: {generated_at.isoformat()}",
        "",
        "이 카탈로그는 공식 `aihubshell`의 메타데이터 출력만 사용해 정리했습니다. "
        "평가 문장은 제목과 파일 트리 기준의 보수적 추정입니다.",
        "",
    ]
    section_titles = {
        "top_opportunity": "## Top Datasets by Opportunity Score",
        "easiest": "## Easiest-Looking Datasets",
        "largest": "## Largest-Looking Datasets",
        "multimodal": "## Multimodal-Looking Datasets",
        "b2b": "## Likely B2B Opportunities",
        "consumer": "## Likely Consumer-App Opportunities",
    }
    for key, title in section_titles.items():
        lines.append(title)
        lines.append("")
        items = sections.get(key, [])
        if not items:
            lines.append("- 해당 조건에 맞는 데이터셋이 아직 없습니다.")
        else:
            lines.extend(_entry_line(item) for item in items)
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def build_catalog_index(settings: ScoutSettings) -> tuple[Path, Path]:
    settings.ensure_directories()
    summaries = load_dataset_summaries(settings)
    generated_at = datetime.now(UTC)

    sections = {
        "top_opportunity": _section_items(summaries, key_name="opportunity_score", reverse=True),
        "easiest": _section_items(summaries, key_name="difficulty_score", reverse=False),
        "largest": _section_items(summaries, key_name="total_size_bytes", reverse=True),
        "multimodal": _filter_multimodal(summaries)[:10],
        "b2b": _filter_b2b(summaries)[:10],
        "consumer": _filter_consumer(summaries)[:10],
    }

    markdown_body = _render_markdown(sections, generated_at)
    markdown_path = catalog_markdown_path(settings)
    write_markdown(markdown_path, markdown_body)

    catalog_payload = {
        "generated_at": generated_at.isoformat(),
        "dataset_count": len(summaries),
        "sections": {
            name: [
                {
                    "dataset_key": item.dataset_key,
                    "title": item.title,
                    "opportunity_score": item.opportunity_score,
                    "difficulty_score": item.difficulty_score,
                    "data_readiness_score": item.data_readiness_score,
                    "human_size": item.human_size,
                    "modality_guess": item.modality_guess,
                    "category_guess": item.category_guess,
                }
                for item in items
            ]
            for name, items in sections.items()
        },
    }
    json_path = write_json(settings.catalog_json_path, catalog_payload)
    return markdown_path, json_path
