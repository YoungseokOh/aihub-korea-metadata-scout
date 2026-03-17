from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from aihub_korea_metadata_scout.models import CommandTrace
from aihub_korea_metadata_scout.shell.parser import (
    parse_dataset_detail_output,
    parse_dataset_list_output,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def fixture_text(path: str) -> str:
    return (FIXTURE_DIR / path).read_text(encoding="utf-8")


def make_trace(command: str) -> CommandTrace:
    return CommandTrace(
        executable="aihubshell",
        args=command.split()[1:],
        command=command,
        exit_code=0,
        collected_at=datetime(2026, 3, 17, 3, 0, 0, tzinfo=UTC),
        stdout_sha256="fixture-sha",
        stderr="",
    )


def test_parse_dataset_list_output_extracts_entries() -> None:
    result = parse_dataset_list_output(
        fixture_text("list/sample_list.txt"),
        make_trace("aihubshell -mode l"),
    )

    assert result.parse_status == "success"
    assert result.dataset_count == 3
    assert result.datasets[0].dataset_key == 86
    assert result.datasets[1].title == "공공행정문서 OCR"
    assert result.datasets[2].raw_title == "지능형 스마트양식장 통합 데이터(가리비)"


def test_parse_dataset_detail_output_extracts_tree_and_files() -> None:
    summary = parse_dataset_detail_output(
        dataset_key=593,
        raw_output=fixture_text("detail/593.txt"),
        trace=make_trace("aihubshell -mode l -datasetkey 593"),
    )

    assert summary.parse_status == "success"
    assert summary.raw_title == "111.지능형 스마트양식장 통합 데이터(가리비)"
    assert summary.file_count == 4
    assert summary.total_size_bytes == (108 + 14) * 1024**2 + 12 * 1024**3
    assert summary.files[0].path.endswith("TL1.zip")
    assert summary.sample_file_paths[1].endswith("TS1.zip")


def test_parse_dataset_detail_output_handles_not_found() -> None:
    summary = parse_dataset_detail_output(
        dataset_key=999999,
        raw_output=fixture_text("detail/not_found.txt"),
        trace=make_trace("aihubshell -mode l -datasetkey 999999"),
    )

    assert summary.parse_status == "error"
    assert summary.file_count == 0
    assert any("페이지가 존재하지 않습니다." in warning for warning in summary.parse_warnings)


def test_parse_dataset_detail_output_captures_notice_lines() -> None:
    summary = parse_dataset_detail_output(
        dataset_key=999,
        raw_output=fixture_text("detail/notice.txt"),
        trace=make_trace("aihubshell -mode l -datasetkey 999"),
    )

    assert summary.parse_status == "success"
    assert summary.notices == ["메타데이터 구조가 변경될 수 있으니 최신 공지를 확인하세요."]
    assert summary.files[0].file_key == 12345
