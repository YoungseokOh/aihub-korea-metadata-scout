from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from aihub_korea_metadata_scout.models import CommandTrace, DatasetFile, DatasetSummary
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
    assert "말뭉치" in dialogue.tags
    assert ocr.category_guess == "ocr/document"
    assert "ocr/document" in ocr.tags
    assert ocr.difficulty_score > dialogue.difficulty_score
    assert ocr.opportunity_score >= 6
    assert dialogue.data_readiness_score >= 6
    assert dialogue.score_reasons
    assert ocr.score_reasons


def test_tag_inference_keeps_meaningful_terms_and_drops_path_noise() -> None:
    summary = DatasetSummary(
        dataset_key=172,
        title="자동차 차종/연식/번호판 인식용 영상",
        raw_title="103.자동차 차종-연식-번호판 인식용 데이터",
        metadata_lines=["추가 데이터 보완 건_211229", "원본이미지 추가개방"],
        files=[
            DatasetFile(
                path=(
                    "103.자동차 차종-연식-번호판 인식용 데이터/"
                    "추가 데이터 보완 건_211229(폴더구조수정)/1.Training/라벨링데이터/"
                    "자동차번호판OCR_training.zip"
                ),
                name="자동차번호판OCR_training.zip",
            ),
            DatasetFile(
                path=(
                    "103.자동차 차종-연식-번호판 인식용 데이터/01.데이터/2.Validation/"
                    "원천데이터/차종분류데이터/SUV.zip"
                ),
                name="SUV.zip",
            ),
        ],
        source_command="aihubshell -mode l -datasetkey 172",
        collected_at="2026-03-17T03:00:00Z",
    )

    summary = enrich_summary(summary)

    assert "번호판" in summary.tags
    assert "자동차" in summary.tags
    assert "ocr/document" in summary.tags
    assert "건" not in summary.tags
    assert "자동차번호판ocr" not in summary.tags
    assert "training" not in summary.tags
