from __future__ import annotations

import re
from datetime import UTC, datetime

from aihub_korea_metadata_scout.config import ConfigurationError, ScoutSettings
from aihub_korea_metadata_scout.models import (
    DatasetEntry,
    DatasetSummary,
    SearchMatch,
    SearchResult,
    path_to_str,
)
from aihub_korea_metadata_scout.pipeline.inspect_dataset import inspect_dataset
from aihub_korea_metadata_scout.pipeline.list_datasets import run_list_datasets
from aihub_korea_metadata_scout.shell.wrapper import AIHubShellWrapper
from aihub_korea_metadata_scout.storage.json_store import load_dataset_summaries

SEARCH_CLEAN_RE = re.compile(r"[^0-9A-Za-z가-힣]+")


def normalize_search_text(text: str) -> str:
    return " ".join(SEARCH_CLEAN_RE.sub(" ", text.casefold()).split())


def search_tokens(query: str) -> list[str]:
    return normalize_search_text(query).split()


def _field_matches_any_token(values: list[str], tokens: list[str]) -> bool:
    combined = normalize_search_text(" ".join(values))
    return any(token in combined for token in tokens)


def _field_matches_all_tokens(values: list[str], tokens: list[str]) -> bool:
    combined = normalize_search_text(" ".join(values))
    return all(token in combined for token in tokens)


def _summary_match_sources(summary: DatasetSummary, tokens: list[str]) -> list[str]:
    field_map = {
        "title": [summary.title, summary.raw_title],
        "tags": summary.tags,
        "category": [summary.category_guess or ""],
        "modality": [summary.modality_guess or ""],
        "metadata": summary.metadata_lines,
        "file-paths": summary.sample_file_paths + [item.path for item in summary.files],
        "notices": summary.notices,
    }
    combined_values: list[str] = []
    for values in field_map.values():
        combined_values.extend(values)
    if not _field_matches_all_tokens(combined_values, tokens):
        return []
    return [name for name, values in field_map.items() if _field_matches_any_token(values, tokens)]


def _entry_match_sources(entry: DatasetEntry, tokens: list[str]) -> list[str]:
    field_map = {
        "title": [entry.title, entry.raw_title],
        "tags": entry.tags,
        "category": [entry.category_guess or ""],
        "modality": [entry.modality_guess or ""],
        "notices": entry.notices,
    }
    combined_values: list[str] = []
    for values in field_map.values():
        combined_values.extend(values)
    if not _field_matches_all_tokens(combined_values, tokens):
        return []
    return [name for name, values in field_map.items() if _field_matches_any_token(values, tokens)]


def _title_match(entry: DatasetEntry, tokens: list[str]) -> bool:
    return _field_matches_all_tokens([entry.title, entry.raw_title], tokens)


def _match_from_summary(summary: DatasetSummary, match_sources: list[str]) -> SearchMatch:
    return SearchMatch(
        dataset_key=summary.dataset_key,
        title=summary.title,
        tags=summary.tags,
        match_sources=sorted(match_sources),
        has_summary=True,
        category_guess=summary.category_guess,
        modality_guess=summary.modality_guess,
        parse_status=summary.parse_status,
        normalized_output_path=summary.normalized_output_path,
        markdown_output_path=summary.markdown_output_path,
    )


def _match_from_entry(entry: DatasetEntry, match_sources: list[str]) -> SearchMatch:
    return SearchMatch(
        dataset_key=entry.dataset_key,
        title=entry.title,
        tags=entry.tags,
        match_sources=sorted(match_sources),
        has_summary=False,
        category_guess=entry.category_guess,
        modality_guess=entry.modality_guess,
        parse_status=entry.parse_status,
    )


def _sorted_matches(matches: list[SearchMatch]) -> list[SearchMatch]:
    return sorted(
        matches,
        key=lambda item: (
            0 if item.has_summary else 1,
            -len(item.match_sources),
            item.dataset_key,
        ),
    )


def search_datasets(
    settings: ScoutSettings,
    query: str,
    *,
    shell: AIHubShellWrapper | None = None,
) -> SearchResult:
    tokens = search_tokens(query)
    if not tokens:
        msg = "Search query must contain letters, numbers, or Korean text."
        raise ConfigurationError(msg)

    settings.ensure_directories()
    wrapper = shell or AIHubShellWrapper(settings)
    listing = run_list_datasets(settings, shell=wrapper)
    existing_summaries = {
        summary.dataset_key: summary for summary in load_dataset_summaries(settings)
    }

    result = SearchResult(
        query=query,
        normalized_query=normalize_search_text(query),
        tokens=tokens,
        source_command=listing.source_command,
        collected_at=datetime.now(UTC),
        total_listed=listing.dataset_count,
        list_output_path=path_to_str(listing.normalized_output_path),
    )

    matches_by_key: dict[int, SearchMatch] = {}
    for summary in existing_summaries.values():
        match_sources = _summary_match_sources(summary, tokens)
        if match_sources:
            matches_by_key[summary.dataset_key] = _match_from_summary(summary, match_sources)

    for entry in listing.datasets:
        if not _title_match(entry, tokens):
            continue

        existing_summary = existing_summaries.get(entry.dataset_key)
        if existing_summary is not None:
            match_sources = _summary_match_sources(existing_summary, tokens)
            if not match_sources:
                match_sources = _entry_match_sources(entry, tokens) or ["title"]
            matches_by_key[entry.dataset_key] = _match_from_summary(existing_summary, match_sources)
            continue

        try:
            summary = inspect_dataset(
                settings,
                entry.dataset_key,
                title_hint=entry.title,
                shell=wrapper,
            )
            result.inspected_during_search.append(entry.dataset_key)
            match_sources = _summary_match_sources(summary, tokens)
            if not match_sources:
                match_sources = _entry_match_sources(entry, tokens) or ["title"]
            matches_by_key[entry.dataset_key] = _match_from_summary(summary, match_sources)
        except Exception as error:  # pragma: no cover - defensive search fallback
            result.search_warnings.append(
                f"{entry.dataset_key}: inspect during search failed: {error}"
            )
            entry_sources = _entry_match_sources(entry, tokens) or ["title"]
            matches_by_key[entry.dataset_key] = _match_from_entry(entry, entry_sources)

    result.matches = _sorted_matches(list(matches_by_key.values()))
    return result
