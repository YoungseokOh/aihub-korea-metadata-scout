from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from aihub_korea_metadata_scout.config import ScoutSettings
from aihub_korea_metadata_scout.models import DatasetListResult, DatasetSummary, ScanResult


def write_json(path: Path, payload: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = payload.model_dump(mode="json") if hasattr(payload, "model_dump") else payload
    path.write_text(json.dumps(body, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def list_result_path(settings: ScoutSettings) -> Path:
    return settings.normalized_list_dir / "latest.json"


def dataset_summary_path(settings: ScoutSettings, dataset_key: int) -> Path:
    return settings.normalized_dataset_dir / f"{dataset_key}.json"


def scan_result_path(settings: ScoutSettings, collected_at: datetime) -> Path:
    timestamp = collected_at.strftime("%Y%m%dT%H%M%SZ")
    return settings.normalized_scan_dir / f"{timestamp}.json"


def write_list_result(settings: ScoutSettings, result: DatasetListResult) -> Path:
    return write_json(list_result_path(settings), result)


def write_dataset_summary(settings: ScoutSettings, summary: DatasetSummary) -> Path:
    return write_json(dataset_summary_path(settings, summary.dataset_key), summary)


def write_scan_result(settings: ScoutSettings, result: ScanResult) -> Path:
    return write_json(scan_result_path(settings, result.collected_at), result)


def load_dataset_summary(path: Path) -> DatasetSummary:
    return DatasetSummary.model_validate_json(path.read_text(encoding="utf-8"))


def load_dataset_summaries(settings: ScoutSettings) -> list[DatasetSummary]:
    if not settings.normalized_dataset_dir.exists():
        return []
    return [
        load_dataset_summary(path)
        for path in sorted(settings.normalized_dataset_dir.glob("*.json"))
    ]
