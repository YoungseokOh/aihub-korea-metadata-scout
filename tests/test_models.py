from __future__ import annotations

from pathlib import Path

from aihub_korea_metadata_scout.config import ScoutSettings
from aihub_korea_metadata_scout.models import (
    DatasetFile,
    DatasetSummary,
    clean_dataset_title,
    humanize_bytes,
    parse_size_to_bytes,
    slugify_title,
)


def test_model_helpers_normalize_titles_and_sizes() -> None:
    assert clean_dataset_title("032.공공행정문서 OCR") == "공공행정문서 OCR"
    assert slugify_title("032.공공행정문서 OCR") == "공공행정문서-ocr"
    assert parse_size_to_bytes("11 GB") == 11 * 1024**3
    assert humanize_bytes(11 * 1024**3).endswith("GB")


def test_dataset_summary_populates_slug_human_size_and_samples() -> None:
    summary = DatasetSummary(
        dataset_key=88,
        title="공공행정문서 OCR",
        raw_title="032.공공행정문서 OCR",
        total_size_bytes=11 * 1024**3,
        source_command="aihubshell -mode l -datasetkey 88",
        collected_at="2026-03-17T03:00:00Z",
        files=[
            DatasetFile(
                path="032.공공행정문서 OCR/01.데이터/[라벨]train.zip",
                name="[라벨]train.zip",
            )
        ],
    )

    assert summary.slug == "공공행정문서-ocr"
    assert summary.human_size.endswith("GB")
    assert summary.sample_file_paths == ["032.공공행정문서 OCR/01.데이터/[라벨]train.zip"]


def test_settings_load_defaults_and_absolute_paths(tmp_path: Path) -> None:
    settings = ScoutSettings(
        output_dir=tmp_path / "artifacts",
        cache_dir=tmp_path / "cache",
        aihub_shell_path=tmp_path / "bin" / "aihubshell",
    )

    settings.ensure_directories()

    assert settings.output_dir.is_absolute()
    assert settings.cache_dir.is_absolute()
    assert settings.normalized_dataset_dir.exists()
    assert settings.generated_index_dir.exists()
