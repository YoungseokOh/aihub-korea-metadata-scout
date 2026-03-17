from __future__ import annotations

from aihub_korea_metadata_scout.config import ScoutSettings
from aihub_korea_metadata_scout.models import DatasetListResult, path_to_str
from aihub_korea_metadata_scout.scoring.heuristics import enrich_entry
from aihub_korea_metadata_scout.shell.parser import parse_dataset_list_output
from aihub_korea_metadata_scout.shell.wrapper import AIHubShellWrapper
from aihub_korea_metadata_scout.storage.cache import write_raw_output
from aihub_korea_metadata_scout.storage.json_store import list_result_path, write_list_result


def run_list_datasets(
    settings: ScoutSettings,
    shell: AIHubShellWrapper | None = None,
) -> DatasetListResult:
    settings.ensure_directories()
    wrapper = shell or AIHubShellWrapper(settings)
    execution = wrapper.run(["-mode", "l"], timeout=120)

    raw_path = write_raw_output(
        settings.raw_list_dir / "latest.txt", execution.stdout, execution.trace
    )
    result = parse_dataset_list_output(execution.stdout, execution.trace)
    result.datasets = [enrich_entry(entry) for entry in result.datasets]

    normalized_path = list_result_path(settings)
    result.raw_output_cache_path = path_to_str(raw_path)
    result.normalized_output_path = path_to_str(normalized_path)
    write_list_result(settings, result)
    return result
