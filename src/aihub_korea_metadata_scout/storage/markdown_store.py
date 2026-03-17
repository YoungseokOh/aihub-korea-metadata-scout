from __future__ import annotations

from pathlib import Path

from aihub_korea_metadata_scout.config import ScoutSettings
from aihub_korea_metadata_scout.models import DatasetSummary


def dataset_markdown_path(settings: ScoutSettings, summary: DatasetSummary) -> Path:
    return settings.generated_dataset_dir / f"{summary.dataset_key}-{summary.slug}.md"


def catalog_markdown_path(settings: ScoutSettings) -> Path:
    return settings.catalog_markdown_path


def write_markdown(path: Path, body: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path
