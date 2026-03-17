from __future__ import annotations

import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from aihub_korea_metadata_scout.config import ScoutSettings
from aihub_korea_metadata_scout.models import DatasetSummary, path_to_str
from aihub_korea_metadata_scout.scoring.business_analysis import apply_business_analysis
from aihub_korea_metadata_scout.storage.json_store import write_dataset_summary
from aihub_korea_metadata_scout.storage.markdown_store import dataset_markdown_path, write_markdown

TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "templates"


def _environment() -> Environment:
    return Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(default_for_string=False),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_dataset_brief(summary: DatasetSummary) -> str:
    if summary.business_opportunity is None:
        summary = apply_business_analysis(summary)
    template = _environment().get_template("dataset_brief.md.j2")
    snapshot_json = json.dumps(summary.compact_snapshot(), ensure_ascii=False, indent=2)
    return template.render(
        summary=summary, opportunity=summary.business_opportunity, snapshot_json=snapshot_json
    )


def generate_dataset_brief(settings: ScoutSettings, summary: DatasetSummary) -> Path:
    settings.ensure_directories()
    body = render_dataset_brief(summary)
    markdown_path = dataset_markdown_path(settings, summary)
    write_markdown(markdown_path, body)
    summary.markdown_output_path = path_to_str(markdown_path)
    write_dataset_summary(settings, summary)
    return markdown_path
