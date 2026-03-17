from __future__ import annotations

import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

ParseStatus = Literal["success", "partial", "error"]

SIZE_UNITS = {
    "B": 1,
    "KB": 1024,
    "MB": 1024**2,
    "GB": 1024**3,
    "TB": 1024**4,
}


def clean_dataset_title(raw_title: str) -> str:
    cleaned = re.sub(r"^\s*\d+\.\s*", "", raw_title).strip()
    return cleaned or raw_title.strip()


def slugify_title(title: str) -> str:
    normalized = clean_dataset_title(title).lower()
    normalized = re.sub(r"[^\w가-힣]+", "-", normalized, flags=re.UNICODE)
    normalized = re.sub(r"-{2,}", "-", normalized).strip("-_")
    return normalized or "dataset"


def parse_size_to_bytes(size_text: str | None) -> int | None:
    if not size_text:
        return None
    match = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*([KMGT]?B)\s*", size_text, flags=re.IGNORECASE)
    if not match:
        return None
    value = float(match.group(1))
    unit = match.group(2).upper()
    return int(value * SIZE_UNITS[unit])


def humanize_bytes(size_bytes: int | None) -> str:
    if size_bytes is None:
        return "unknown"
    if size_bytes == 0:
        return "0 B"
    value = float(size_bytes)
    unit = "B"
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            break
        value /= 1024
    formatted = f"{value:.1f}" if value >= 10 or unit == "B" else f"{value:.2f}"
    if unit == "B":
        formatted = str(int(value))
    return f"{formatted} {unit}"


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class BaseScoutModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class CommandTrace(BaseScoutModel):
    executable: str
    args: list[str]
    command: str
    exit_code: int
    collected_at: datetime
    stdout_sha256: str
    stderr: str = ""


class DatasetEntry(BaseScoutModel):
    dataset_key: int
    title: str
    raw_title: str
    slug: str | None = None
    tags: list[str] = Field(default_factory=list)
    category_guess: str | None = None
    modality_guess: str | None = None
    notices: list[str] = Field(default_factory=list)
    source_command: str
    collected_at: datetime
    parse_status: ParseStatus = "success"
    parse_warnings: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def populate_defaults(self) -> DatasetEntry:
        if not self.title:
            self.title = clean_dataset_title(self.raw_title)
        if not self.raw_title:
            self.raw_title = self.title
        if self.slug is None:
            self.slug = slugify_title(self.title)
        return self


class DatasetFile(BaseScoutModel):
    path: str
    name: str
    parent_path: str | None = None
    size_text: str | None = None
    size_bytes: int | None = None
    file_key: int | None = None
    depth: int = 0


class DatasetTree(BaseScoutModel):
    root_name: str | None = None
    directory_paths: list[str] = Field(default_factory=list)
    files: list[DatasetFile] = Field(default_factory=list)
    file_tree_lines: list[str] = Field(default_factory=list)
    metadata_lines: list[str] = Field(default_factory=list)
    notices: list[str] = Field(default_factory=list)


class BusinessOpportunity(BaseScoutModel):
    inferred_summary: str
    business_use_cases: list[str] = Field(default_factory=list)
    customer_segments: list[str] = Field(default_factory=list)
    monetization_models: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    why_interesting: list[str] = Field(default_factory=list)
    why_it_might_fail: list[str] = Field(default_factory=list)
    practicality_assessment: list[str] = Field(default_factory=list)
    legal_caution: str = "License and policy suitability must be validated separately."
    opportunity_score: int = Field(ge=1, le=10)
    difficulty_score: int = Field(ge=1, le=10)
    data_readiness_score: int = Field(ge=1, le=10)
    score_reasons: list[str] = Field(default_factory=list)


class DatasetSummary(BaseScoutModel):
    dataset_key: int
    title: str
    raw_title: str
    slug: str | None = None
    tags: list[str] = Field(default_factory=list)
    category_guess: str | None = None
    modality_guess: str | None = None
    file_count: int = 0
    total_size_bytes: int | None = None
    human_size: str | None = None
    sample_file_paths: list[str] = Field(default_factory=list)
    notices: list[str] = Field(default_factory=list)
    source_command: str
    collected_at: datetime
    parse_status: ParseStatus = "success"
    parse_warnings: list[str] = Field(default_factory=list)
    inferred_summary: str = ""
    business_use_cases: list[str] = Field(default_factory=list)
    customer_segments: list[str] = Field(default_factory=list)
    monetization_models: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    difficulty_score: int = Field(default=5, ge=1, le=10)
    opportunity_score: int = Field(default=5, ge=1, le=10)
    data_readiness_score: int = Field(default=5, ge=1, le=10)
    score_reasons: list[str] = Field(default_factory=list)
    files: list[DatasetFile] = Field(default_factory=list)
    tree: DatasetTree = Field(default_factory=DatasetTree)
    metadata_lines: list[str] = Field(default_factory=list)
    business_opportunity: BusinessOpportunity | None = None
    raw_output_cache_path: str | None = None
    normalized_output_path: str | None = None
    markdown_output_path: str | None = None

    @model_validator(mode="after")
    def populate_defaults(self) -> DatasetSummary:
        if self.slug is None:
            self.slug = slugify_title(self.title or self.raw_title)
        if self.human_size is None:
            self.human_size = humanize_bytes(self.total_size_bytes)
        if not self.sample_file_paths:
            self.sample_file_paths = [item.path for item in self.files[:5]]
        return self

    def compact_snapshot(self) -> dict[str, Any]:
        return {
            "dataset_key": self.dataset_key,
            "title": self.title,
            "tags": self.tags[:10],
            "category_guess": self.category_guess,
            "modality_guess": self.modality_guess,
            "file_count": self.file_count,
            "total_size_bytes": self.total_size_bytes,
            "human_size": self.human_size,
            "sample_file_paths": self.sample_file_paths[:5],
            "parse_status": self.parse_status,
            "parse_warnings": self.parse_warnings[:5],
            "notices": self.notices[:5],
        }


class DatasetListResult(BaseScoutModel):
    source_command: str
    collected_at: datetime
    parse_status: ParseStatus
    parse_warnings: list[str] = Field(default_factory=list)
    dataset_count: int
    datasets: list[DatasetEntry] = Field(default_factory=list)
    raw_output_cache_path: str | None = None
    normalized_output_path: str | None = None


class SearchMatch(BaseScoutModel):
    dataset_key: int
    title: str
    tags: list[str] = Field(default_factory=list)
    match_sources: list[str] = Field(default_factory=list)
    has_summary: bool = False
    category_guess: str | None = None
    modality_guess: str | None = None
    parse_status: ParseStatus = "success"
    normalized_output_path: str | None = None
    markdown_output_path: str | None = None


class SearchResult(BaseScoutModel):
    query: str
    normalized_query: str
    tokens: list[str] = Field(default_factory=list)
    source_command: str
    collected_at: datetime
    total_listed: int = 0
    list_output_path: str | None = None
    inspected_during_search: list[int] = Field(default_factory=list)
    search_warnings: list[str] = Field(default_factory=list)
    matches: list[SearchMatch] = Field(default_factory=list)

    @property
    def total_matches(self) -> int:
        return len(self.matches)


class ScanResult(BaseScoutModel):
    source_command: str
    collected_at: datetime
    limit: int | None = None
    total_listed: int = 0
    processed: int = 0
    skipped: int = 0
    failed: int = 0
    dataset_keys: list[int] = Field(default_factory=list)
    generated_markdown_files: list[str] = Field(default_factory=list)
    parse_warnings: list[str] = Field(default_factory=list)
    list_output_path: str | None = None
    scan_output_path: str | None = None
    catalog_output_path: str | None = None
    catalog_json_path: str | None = None


def path_to_str(path: Path | None) -> str | None:
    return str(path) if path is not None else None
