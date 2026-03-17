from __future__ import annotations

import re
from collections.abc import Iterable

from aihub_korea_metadata_scout.models import (
    CommandTrace,
    DatasetEntry,
    DatasetFile,
    DatasetListResult,
    DatasetSummary,
    DatasetTree,
    clean_dataset_title,
    humanize_bytes,
    parse_size_to_bytes,
)

LIST_LINE_RE = re.compile(r"^\s*(?P<dataset_key>\d+)\s*,\s*(?P<title>.+?)\s*$")
TREE_LINE_RE = re.compile(r"^(?P<prefix>(?: {4}|│ {2})*)(?P<branch>[├└]─)\s*(?P<body>.+?)\s*$")
FILE_LINE_RE = re.compile(r"^(?P<name>.+?)\s*\|\s*(?P<size>[^\|]+?)\s*\|\s*(?P<file_key>\d+)\s*$")

LIST_BANNER_MARKERS = (
    "aihubshell version",
    "Fetching dataset information...",
    "DataSet 목록",
)
DETAIL_BANNER_MARKERS = (
    "aihubshell version",
    "Fetching file tree structure...",
    "The contents are encoded in UTF-8 including Korean characters.",
    "If the following contents are not output normally,",
    "Please modify the character information of the OS.",
)
NOT_FOUND_MARKERS = ("페이지가 존재하지 않습니다.",)


def _is_separator(line: str) -> bool:
    stripped = line.strip()
    return bool(stripped) and set(stripped) == {"="}


def _is_banner_line(line: str, markers: Iterable[str]) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if _is_separator(stripped):
        return True
    return any(marker in stripped for marker in markers)


def _tree_depth(prefix: str) -> int:
    groups = re.findall(r"(?: {4}|│ {2})", prefix)
    return max(len(groups) - 1, 0)


def parse_dataset_list_output(raw_output: str, trace: CommandTrace) -> DatasetListResult:
    entries: list[DatasetEntry] = []
    warnings: list[str] = []

    for raw_line in raw_output.splitlines():
        line = raw_line.rstrip()
        if _is_banner_line(line, LIST_BANNER_MARKERS):
            continue
        match = LIST_LINE_RE.match(line)
        if match:
            raw_title = match.group("title").strip()
            entries.append(
                DatasetEntry(
                    dataset_key=int(match.group("dataset_key")),
                    title=clean_dataset_title(raw_title),
                    raw_title=raw_title,
                    source_command=trace.command,
                    collected_at=trace.collected_at,
                )
            )
            continue
        warnings.append(f"Unparsed list line: {line.strip()}")

    if not entries:
        status = "error"
    elif warnings:
        status = "partial"
    else:
        status = "success"

    return DatasetListResult(
        source_command=trace.command,
        collected_at=trace.collected_at,
        parse_status=status,
        parse_warnings=warnings,
        dataset_count=len(entries),
        datasets=entries,
    )


def parse_dataset_detail_output(
    dataset_key: int,
    raw_output: str,
    trace: CommandTrace,
    title_hint: str | None = None,
) -> DatasetSummary:
    warnings: list[str] = []
    notices: list[str] = []
    metadata_lines: list[str] = []
    tree_lines: list[str] = []
    files: list[DatasetFile] = []
    directory_paths: list[str] = []
    stack: list[str] = []
    root_name: str | None = None
    capture_notices = False

    for raw_line in raw_output.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if any(marker in stripped for marker in NOT_FOUND_MARKERS):
            warnings.append(stripped)
            metadata_lines.append(stripped)
            continue

        if "공지사항" in stripped:
            capture_notices = True
            continue

        tree_match = TREE_LINE_RE.match(line)
        if tree_match:
            capture_notices = False
            prefix = tree_match.group("prefix")
            body = tree_match.group("body").strip()
            depth = _tree_depth(prefix)
            tree_lines.append(line)

            if depth > len(stack):
                warnings.append(f"Adjusted unexpected tree depth for line: {body}")
                depth = len(stack)

            file_match = FILE_LINE_RE.match(body)
            if file_match:
                file_name = file_match.group("name").strip()
                size_text = file_match.group("size").strip()
                file_key = int(file_match.group("file_key"))
                parent_parts = stack[:depth]
                path_parts = [*parent_parts, file_name]
                parent_path = "/".join(parent_parts) if parent_parts else None
                files.append(
                    DatasetFile(
                        path="/".join(path_parts),
                        name=file_name,
                        parent_path=parent_path,
                        size_text=size_text,
                        size_bytes=parse_size_to_bytes(size_text),
                        file_key=file_key,
                        depth=depth,
                    )
                )
                continue

            stack = [*stack[:depth], body]
            directory_paths.append("/".join(stack))
            if root_name is None:
                root_name = body
            continue

        if _is_banner_line(line, DETAIL_BANNER_MARKERS):
            continue

        if capture_notices and stripped:
            notices.append(stripped)
            continue

        if stripped:
            metadata_lines.append(stripped)
            warnings.append(f"Unparsed detail line: {stripped}")

    total_size_bytes = sum(file.size_bytes or 0 for file in files) if files else None
    raw_title = root_name or title_hint or f"Dataset {dataset_key}"
    title = clean_dataset_title(title_hint or raw_title)

    if not files and any(marker in raw_output for marker in NOT_FOUND_MARKERS):
        parse_status = "error"
    elif warnings:
        parse_status = "partial"
    else:
        parse_status = "success"

    return DatasetSummary(
        dataset_key=dataset_key,
        title=title,
        raw_title=raw_title,
        category_guess=None,
        modality_guess=None,
        file_count=len(files),
        total_size_bytes=total_size_bytes,
        human_size=humanize_bytes(total_size_bytes),
        sample_file_paths=[item.path for item in files[:5]],
        notices=notices,
        source_command=trace.command,
        collected_at=trace.collected_at,
        parse_status=parse_status,
        parse_warnings=warnings,
        files=files,
        tree=DatasetTree(
            root_name=root_name,
            directory_paths=directory_paths,
            files=files,
            file_tree_lines=tree_lines,
            metadata_lines=metadata_lines,
            notices=notices,
        ),
        metadata_lines=metadata_lines,
    )
