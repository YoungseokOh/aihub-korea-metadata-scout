from __future__ import annotations

from pathlib import Path

from aihub_korea_metadata_scout.config import ScoutSettings
from aihub_korea_metadata_scout.models import DatasetSummary, path_to_str
from aihub_korea_metadata_scout.scoring.business_analysis import apply_business_analysis
from aihub_korea_metadata_scout.scoring.heuristics import enrich_summary
from aihub_korea_metadata_scout.shell.parser import parse_dataset_detail_output
from aihub_korea_metadata_scout.shell.wrapper import AIHubShellWrapper
from aihub_korea_metadata_scout.storage.cache import write_raw_output
from aihub_korea_metadata_scout.storage.json_store import (
    dataset_summary_path,
    load_dataset_summary,
    write_dataset_summary,
)


def load_existing_summary(settings: ScoutSettings, dataset_key: int) -> DatasetSummary | None:
    path = dataset_summary_path(settings, dataset_key)
    if not path.exists():
        return None
    return load_dataset_summary(path)


def inspect_dataset(
    settings: ScoutSettings,
    dataset_key: int,
    title_hint: str | None = None,
    shell: AIHubShellWrapper | None = None,
) -> DatasetSummary:
    settings.ensure_directories()
    wrapper = shell or AIHubShellWrapper(settings)
    execution = wrapper.run(["-mode", "l", "-datasetkey", str(dataset_key)], timeout=120)

    raw_path = write_raw_output(
        settings.raw_dataset_dir / f"{dataset_key}.txt",
        execution.stdout,
        execution.trace,
    )
    summary = parse_dataset_detail_output(
        dataset_key=dataset_key,
        raw_output=execution.stdout,
        trace=execution.trace,
        title_hint=title_hint,
    )
    summary = enrich_summary(summary)
    summary = apply_business_analysis(summary)

    normalized_path = dataset_summary_path(settings, dataset_key)
    summary.raw_output_cache_path = path_to_str(raw_path)
    summary.normalized_output_path = path_to_str(normalized_path)
    write_dataset_summary(settings, summary)
    return summary


def normalized_summary_exists(settings: ScoutSettings, dataset_key: int) -> bool:
    return dataset_summary_path(settings, dataset_key).exists()


def normalized_summary_file(settings: ScoutSettings, dataset_key: int) -> Path:
    return dataset_summary_path(settings, dataset_key)
