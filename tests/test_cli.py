from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from typer.testing import CliRunner

from aihub_korea_metadata_scout.cli import app
from aihub_korea_metadata_scout.config import ScoutSettings
from aihub_korea_metadata_scout.models import (
    BusinessOpportunity,
    DatasetEntry,
    DatasetListResult,
    DatasetSummary,
)
from aihub_korea_metadata_scout.shell.install import InstallResult

runner = CliRunner()


def settings_for(tmp_path: Path) -> ScoutSettings:
    return ScoutSettings(output_dir=tmp_path / "data", cache_dir=tmp_path / "data" / "raw")


def sample_list_result() -> DatasetListResult:
    return DatasetListResult(
        source_command="aihubshell -mode l",
        collected_at=datetime(2026, 3, 17, 3, 0, 0, tzinfo=UTC),
        parse_status="success",
        dataset_count=2,
        datasets=[
            DatasetEntry(
                dataset_key=86,
                title="감성 대화 말뭉치",
                raw_title="감성 대화 말뭉치",
                source_command="aihubshell -mode l",
                collected_at=datetime(2026, 3, 17, 3, 0, 0, tzinfo=UTC),
            ),
            DatasetEntry(
                dataset_key=88,
                title="공공행정문서 OCR",
                raw_title="공공행정문서 OCR",
                source_command="aihubshell -mode l",
                collected_at=datetime(2026, 3, 17, 3, 0, 0, tzinfo=UTC),
            ),
        ],
        normalized_output_path="/tmp/latest.json",
    )


def sample_summary() -> DatasetSummary:
    opportunity = BusinessOpportunity(
        inferred_summary="요약입니다. inferred from title and file tree only.",
        business_use_cases=["문서 자동화"],
        customer_segments=["공공기관"],
        monetization_models=["엔터프라이즈 구독"],
        risks=["정책 검토 필요"],
        why_interesting=["문제 정의가 선명합니다."],
        why_it_might_fail=["실제 품질은 미확인입니다."],
        practicality_assessment=["전처리 자동화가 필요합니다."],
        opportunity_score=8,
        difficulty_score=7,
        data_readiness_score=7,
        score_reasons=["라벨 구조가 보입니다."],
    )
    return DatasetSummary(
        dataset_key=88,
        title="공공행정문서 OCR",
        raw_title="032.공공행정문서 OCR",
        file_count=23,
        total_size_bytes=100,
        human_size="100 B",
        sample_file_paths=["032.공공행정문서 OCR/01.데이터/[라벨]train.zip"],
        source_command="aihubshell -mode l -datasetkey 88",
        collected_at=datetime(2026, 3, 17, 3, 0, 0, tzinfo=UTC),
        parse_status="success",
        inferred_summary=opportunity.inferred_summary,
        business_use_cases=opportunity.business_use_cases,
        customer_segments=opportunity.customer_segments,
        monetization_models=opportunity.monetization_models,
        risks=opportunity.risks,
        difficulty_score=opportunity.difficulty_score,
        opportunity_score=opportunity.opportunity_score,
        data_readiness_score=opportunity.data_readiness_score,
        score_reasons=opportunity.score_reasons,
        business_opportunity=opportunity,
        normalized_output_path="/tmp/88.json",
    )


def test_bootstrap_command_reports_install(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("aihub_korea_metadata_scout.cli._settings", lambda: settings_for(tmp_path))
    monkeypatch.setattr(
        "aihub_korea_metadata_scout.cli.install_aihubshell",
        lambda settings, force=False: InstallResult(
            path=tmp_path / "bin" / "aihubshell",
            installed=True,
            verified=True,
            verification_output="aihubshell version 25.09.19 v0.6",
            path_guidance=None,
        ),
    )

    result = runner.invoke(app, ["bootstrap"])

    assert result.exit_code == 0
    assert "aihubshell installed" in result.stdout


def test_doctor_command_happy_path(monkeypatch, tmp_path: Path) -> None:
    settings = settings_for(tmp_path)
    monkeypatch.setattr("aihub_korea_metadata_scout.cli._settings", lambda: settings)
    monkeypatch.setattr(
        ScoutSettings,
        "current_python_version",
        staticmethod(lambda: (3, 11, 15)),
    )
    monkeypatch.setattr(
        "aihub_korea_metadata_scout.cli.resolve_shell_path",
        lambda _: tmp_path / "bin" / "aihubshell",
    )
    monkeypatch.setattr(
        "aihub_korea_metadata_scout.cli.AIHubShellWrapper.verify_metadata_access",
        lambda self: None,
    )

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "Environment Doctor" in result.stdout
    assert "Metadata list command" in result.stdout


def test_doctor_command_reports_python_version_failure(monkeypatch, tmp_path: Path) -> None:
    settings = settings_for(tmp_path)
    monkeypatch.setattr("aihub_korea_metadata_scout.cli._settings", lambda: settings)
    monkeypatch.setattr(
        ScoutSettings,
        "current_python_version",
        staticmethod(lambda: (3, 10, 12)),
    )
    monkeypatch.setattr(
        "aihub_korea_metadata_scout.cli.resolve_shell_path",
        lambda _: tmp_path / "bin" / "aihubshell",
    )
    monkeypatch.setattr(
        "aihub_korea_metadata_scout.cli.AIHubShellWrapper.verify_metadata_access",
        lambda self: None,
    )

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 1
    assert "Python 3.11+" in result.stdout
    assert "uv python install 3.11" in result.stdout
    assert "Metadata list command" in result.stdout


def test_list_command_prints_rows(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "aihub_korea_metadata_scout.cli._require_runtime", lambda: settings_for(tmp_path)
    )
    monkeypatch.setattr(
        "aihub_korea_metadata_scout.cli.run_list_datasets", lambda settings: sample_list_result()
    )

    result = runner.invoke(app, ["list", "--limit", "1"])

    assert result.exit_code == 0
    assert "AI-Hub Dataset Listings" in result.stdout
    assert "감성 대화 말뭉치" in result.stdout


def test_list_command_fails_for_unsupported_python(monkeypatch) -> None:
    monkeypatch.setattr(
        ScoutSettings,
        "current_python_version",
        staticmethod(lambda: (3, 10, 12)),
    )

    result = runner.invoke(app, ["list"])

    assert result.exit_code == 1
    assert "Python 3.11+ is required" in result.stdout
    assert "uv sync --python 3.11" in result.stdout


def test_summarize_command_reports_paths(monkeypatch, tmp_path: Path) -> None:
    settings = settings_for(tmp_path)
    monkeypatch.setattr("aihub_korea_metadata_scout.cli._require_runtime", lambda: settings)
    monkeypatch.setattr(
        "aihub_korea_metadata_scout.cli.inspect_dataset",
        lambda settings, datasetkey: sample_summary(),
    )
    monkeypatch.setattr(
        "aihub_korea_metadata_scout.cli.generate_dataset_brief",
        lambda settings, summary: (
            tmp_path / "data" / "generated" / "datasets" / "88-공공행정문서-ocr.md"
        ),
    )

    result = runner.invoke(app, ["summarize", "--datasetkey", "88"])

    assert result.exit_code == 0
    assert "Saved JSON to /tmp/88.json" in result.stdout
    assert "88-공공행정문서-ocr.md" in result.stdout


def test_scan_command_uses_existing_summaries_and_builds_catalog(
    monkeypatch, tmp_path: Path
) -> None:
    settings = settings_for(tmp_path)
    monkeypatch.setattr("aihub_korea_metadata_scout.cli._require_runtime", lambda: settings)
    monkeypatch.setattr(
        "aihub_korea_metadata_scout.cli.run_list_datasets", lambda settings: sample_list_result()
    )
    monkeypatch.setattr(
        "aihub_korea_metadata_scout.cli.load_existing_summary",
        lambda settings, dataset_key: sample_summary(),
    )
    monkeypatch.setattr(
        "aihub_korea_metadata_scout.cli.generate_dataset_brief",
        lambda settings, summary: (
            tmp_path / "data" / "generated" / "datasets" / "88-공공행정문서-ocr.md"
        ),
    )
    monkeypatch.setattr(
        "aihub_korea_metadata_scout.cli.build_catalog_index",
        lambda settings: (
            tmp_path / "data" / "generated" / "index" / "dataset-catalog.md",
            tmp_path / "data" / "normalized" / "catalog.json",
        ),
    )
    monkeypatch.setattr(
        "aihub_korea_metadata_scout.cli.write_scan_result",
        lambda settings, result: tmp_path / "data" / "normalized" / "scans" / "scan.json",
    )

    result = runner.invoke(app, ["scan", "--limit", "2"])

    assert result.exit_code == 0
    assert "Selected=2" in result.stdout
    assert "Skipped=2" in result.stdout
    assert "dataset-catalog.md" in result.stdout


def test_scan_command_supports_all_flag(monkeypatch, tmp_path: Path) -> None:
    settings = settings_for(tmp_path)
    monkeypatch.setattr("aihub_korea_metadata_scout.cli._require_runtime", lambda: settings)
    monkeypatch.setattr(
        "aihub_korea_metadata_scout.cli.run_list_datasets", lambda settings: sample_list_result()
    )
    monkeypatch.setattr(
        "aihub_korea_metadata_scout.cli.load_existing_summary",
        lambda settings, dataset_key: sample_summary(),
    )
    monkeypatch.setattr(
        "aihub_korea_metadata_scout.cli.generate_dataset_brief",
        lambda settings, summary: (
            tmp_path / "data" / "generated" / "datasets" / "88-공공행정문서-ocr.md"
        ),
    )
    monkeypatch.setattr(
        "aihub_korea_metadata_scout.cli.build_catalog_index",
        lambda settings: (
            tmp_path / "data" / "generated" / "index" / "dataset-catalog.md",
            tmp_path / "data" / "normalized" / "catalog.json",
        ),
    )
    monkeypatch.setattr(
        "aihub_korea_metadata_scout.cli.write_scan_result",
        lambda settings, result: tmp_path / "data" / "normalized" / "scans" / "scan.json",
    )

    result = runner.invoke(app, ["scan", "--all"])

    assert result.exit_code == 0
    assert "Selected=2" in result.stdout
    assert "Skipped=2" in result.stdout
