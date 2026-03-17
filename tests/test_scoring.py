from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from aihub_korea_metadata_scout.models import CommandTrace
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


def build_summary(dataset_key: int, fixture_name: str):
    raw = (FIXTURE_DIR / "detail" / fixture_name).read_text(encoding="utf-8")
    summary = parse_dataset_detail_output(dataset_key, raw, make_trace(dataset_key))
    summary = enrich_summary(summary)
    return apply_business_analysis(summary)


def test_scoring_marks_large_ocr_dataset_as_harder_than_small_dialogue_dataset() -> None:
    dialogue = build_summary(86, "86.txt")
    ocr = build_summary(88, "88.txt")

    assert dialogue.modality_guess == "text"
    assert ocr.category_guess == "ocr/document"
    assert ocr.difficulty_score > dialogue.difficulty_score
    assert ocr.opportunity_score >= 6
    assert dialogue.data_readiness_score >= 6
    assert dialogue.score_reasons
    assert ocr.score_reasons
