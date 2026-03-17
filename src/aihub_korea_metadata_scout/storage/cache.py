from __future__ import annotations

import json
from pathlib import Path

from aihub_korea_metadata_scout.models import CommandTrace


def _write_trace_sidecar(path: Path, trace: CommandTrace) -> None:
    sidecar_path = path.with_suffix(".meta.json")
    sidecar_path.write_text(
        json.dumps(trace.model_dump(mode="json"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def write_raw_output(path: Path, output: str, trace: CommandTrace) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(output, encoding="utf-8")
    _write_trace_sidecar(path, trace)
    return path
