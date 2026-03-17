from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from aihub_korea_metadata_scout.config import ScoutSettings
from aihub_korea_metadata_scout.models import DatasetEntry, DatasetListResult, DatasetSummary
from aihub_korea_metadata_scout.pipeline.search_datasets import search_datasets


def settings_for(tmp_path: Path) -> ScoutSettings:
    return ScoutSettings(output_dir=tmp_path / "data", cache_dir=tmp_path / "data" / "raw")


def make_listing(*entries: DatasetEntry) -> DatasetListResult:
    return DatasetListResult(
        source_command="aihubshell -mode l",
        collected_at=datetime(2026, 3, 17, 3, 0, 0, tzinfo=UTC),
        parse_status="success",
        dataset_count=len(entries),
        datasets=list(entries),
        normalized_output_path="/tmp/latest.json",
    )


def make_entry(dataset_key: int, title: str, tags: list[str] | None = None) -> DatasetEntry:
    return DatasetEntry(
        dataset_key=dataset_key,
        title=title,
        raw_title=title,
        tags=tags or [],
        source_command="aihubshell -mode l",
        collected_at=datetime(2026, 3, 17, 3, 0, 0, tzinfo=UTC),
    )


def make_summary(
    dataset_key: int,
    title: str,
    *,
    tags: list[str] | None = None,
    metadata_lines: list[str] | None = None,
) -> DatasetSummary:
    return DatasetSummary(
        dataset_key=dataset_key,
        title=title,
        raw_title=title,
        tags=tags or [],
        metadata_lines=metadata_lines or [],
        source_command=f"aihubshell -mode l -datasetkey {dataset_key}",
        collected_at=datetime(2026, 3, 17, 3, 0, 0, tzinfo=UTC),
        normalized_output_path=f"/tmp/{dataset_key}.json",
    )


def test_search_uses_existing_summary_tags(monkeypatch, tmp_path: Path) -> None:
    settings = settings_for(tmp_path)
    entry = make_entry(301, "차량 이미지 데이터")
    summary = make_summary(301, "차량 이미지 데이터", tags=["번호판", "image"])

    monkeypatch.setattr(
        "aihub_korea_metadata_scout.pipeline.search_datasets.run_list_datasets",
        lambda settings, shell=None: make_listing(entry),
    )
    monkeypatch.setattr(
        "aihub_korea_metadata_scout.pipeline.search_datasets.load_dataset_summaries",
        lambda settings: [summary],
    )

    result = search_datasets(settings, "번호판", shell=object())

    assert result.total_matches == 1
    assert result.matches[0].dataset_key == 301
    assert result.matches[0].has_summary is True
    assert "tags" in result.matches[0].match_sources


def test_search_inspects_title_matches_without_existing_summary(
    monkeypatch, tmp_path: Path
) -> None:
    settings = settings_for(tmp_path)
    entry = make_entry(302, "번호판 검출 이미지")
    summary = make_summary(302, "번호판 검출 이미지", tags=["번호판", "image"])

    monkeypatch.setattr(
        "aihub_korea_metadata_scout.pipeline.search_datasets.run_list_datasets",
        lambda settings, shell=None: make_listing(entry),
    )
    monkeypatch.setattr(
        "aihub_korea_metadata_scout.pipeline.search_datasets.load_dataset_summaries",
        lambda settings: [],
    )
    monkeypatch.setattr(
        "aihub_korea_metadata_scout.pipeline.search_datasets.inspect_dataset",
        lambda settings, dataset_key, title_hint=None, shell=None: summary,
    )

    result = search_datasets(settings, "번호판", shell=object())

    assert result.total_matches == 1
    assert result.inspected_during_search == [302]
    assert result.matches[0].has_summary is True
    assert result.matches[0].dataset_key == 302


def test_search_deduplicates_existing_summary_and_title_match(monkeypatch, tmp_path: Path) -> None:
    settings = settings_for(tmp_path)
    entry = make_entry(303, "번호판 OCR", tags=["번호판"])
    summary = make_summary(303, "번호판 OCR", tags=["번호판", "ocr/document"])

    monkeypatch.setattr(
        "aihub_korea_metadata_scout.pipeline.search_datasets.run_list_datasets",
        lambda settings, shell=None: make_listing(entry),
    )
    monkeypatch.setattr(
        "aihub_korea_metadata_scout.pipeline.search_datasets.load_dataset_summaries",
        lambda settings: [summary],
    )

    result = search_datasets(settings, "번호판", shell=object())

    assert result.total_matches == 1
    assert result.matches[0].dataset_key == 303
    assert result.inspected_during_search == []


def test_search_returns_no_matches_when_query_is_absent(monkeypatch, tmp_path: Path) -> None:
    settings = settings_for(tmp_path)
    entry = make_entry(304, "감성 대화 말뭉치")

    monkeypatch.setattr(
        "aihub_korea_metadata_scout.pipeline.search_datasets.run_list_datasets",
        lambda settings, shell=None: make_listing(entry),
    )
    monkeypatch.setattr(
        "aihub_korea_metadata_scout.pipeline.search_datasets.load_dataset_summaries",
        lambda settings: [],
    )

    result = search_datasets(settings, "번호판", shell=object())

    assert result.total_matches == 0
    assert result.matches == []
