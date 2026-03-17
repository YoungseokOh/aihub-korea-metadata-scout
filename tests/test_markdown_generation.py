from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from aihub_korea_metadata_scout.config import ScoutSettings
from aihub_korea_metadata_scout.models import CommandTrace
from aihub_korea_metadata_scout.pipeline.generate_markdown import (
    generate_dataset_brief,
    render_dataset_brief,
)
from aihub_korea_metadata_scout.scoring.business_analysis import apply_business_analysis
from aihub_korea_metadata_scout.scoring.heuristics import enrich_summary
from aihub_korea_metadata_scout.shell.parser import parse_dataset_detail_output

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def make_trace(dataset_key: int) -> CommandTrace:
    return CommandTrace(
        executable="aihubshell",
        args=["-mode", "l", "-datasetkey", str(dataset_key)],
        command=f"aihubshell -mode l -datasetkey {dataset_key}",
        exit_code=0,
        collected_at=datetime(2026, 3, 17, 3, 0, 0, tzinfo=UTC),
        stdout_sha256="fixture-sha",
        stderr="",
    )


def build_summary(dataset_key: int, name: str) -> object:
    raw = (FIXTURE_DIR / "detail" / name).read_text(encoding="utf-8")
    summary = parse_dataset_detail_output(dataset_key, raw, make_trace(dataset_key))
    summary = enrich_summary(summary)
    return apply_business_analysis(summary)


def test_render_dataset_brief_contains_required_sections() -> None:
    summary = build_summary(86, "86.txt")
    markdown = render_dataset_brief(summary)

    assert "# 감성대화" in markdown
    assert "## Basic Info" in markdown
    assert "Inferred tags" in markdown
    assert "## Scores" in markdown
    assert "inferred from title and file tree only" in markdown
    assert "```json" in markdown


def test_generate_dataset_brief_writes_expected_path(tmp_path: Path) -> None:
    settings = ScoutSettings(output_dir=tmp_path / "data", cache_dir=tmp_path / "data" / "raw")
    summary = build_summary(88, "88.txt")

    markdown_path = generate_dataset_brief(settings, summary)

    assert markdown_path.name == "88-공공행정문서-ocr.md"
    assert markdown_path.exists()
    body = markdown_path.read_text(encoding="utf-8")
    assert "공공행정문서 OCR" in body
    assert "Opportunity score" in body
