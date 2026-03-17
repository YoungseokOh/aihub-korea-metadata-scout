from __future__ import annotations

from datetime import UTC, datetime

import typer
from rich.console import Console
from rich.progress import track
from rich.table import Table

from aihub_korea_metadata_scout.config import (
    MINIMUM_PYTHON_LABEL,
    ConfigurationError,
    ScoutSettings,
    get_settings,
)
from aihub_korea_metadata_scout.logging import configure_logging, get_logger
from aihub_korea_metadata_scout.models import ScanResult, path_to_str
from aihub_korea_metadata_scout.pipeline.build_catalog import build_catalog_index
from aihub_korea_metadata_scout.pipeline.generate_markdown import generate_dataset_brief
from aihub_korea_metadata_scout.pipeline.inspect_dataset import (
    inspect_dataset,
    load_existing_summary,
)
from aihub_korea_metadata_scout.pipeline.list_datasets import run_list_datasets
from aihub_korea_metadata_scout.shell.install import InstallationError, install_aihubshell
from aihub_korea_metadata_scout.shell.wrapper import (
    AIHubShellWrapper,
    ShellExecutionError,
    resolve_shell_path,
)
from aihub_korea_metadata_scout.storage.json_store import write_scan_result

app = typer.Typer(no_args_is_help=True, help="Metadata-only AI-Hub Korea dataset scout.")
console = Console()
logger = get_logger(__name__)


def _settings() -> ScoutSettings:
    settings = get_settings()
    settings.ensure_directories()
    return settings


def _require_runtime() -> ScoutSettings:
    ScoutSettings.validate_python_version()
    return _settings()


def _handle_error(error: Exception) -> None:
    console.print(f"[red]{error}[/red]")
    raise typer.Exit(code=1) from error


def _print_list_table(dataset_rows: list[tuple[int, str, str | None, str | None]]) -> None:
    table = Table(title="AI-Hub Dataset Listings")
    table.add_column("Dataset Key", justify="right")
    table.add_column("Title")
    table.add_column("Category")
    table.add_column("Modality")
    for dataset_key, title, category, modality in dataset_rows:
        table.add_row(str(dataset_key), title, category or "-", modality or "-")
    console.print(table)


def _print_summary_table(summary) -> None:
    table = Table(title=f"Dataset {summary.dataset_key}")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Title", summary.title)
    table.add_row("Parse Status", summary.parse_status)
    table.add_row("Category", summary.category_guess or "-")
    table.add_row("Modality", summary.modality_guess or "-")
    table.add_row("File Count", str(summary.file_count))
    table.add_row("Known Size", summary.human_size or "unknown")
    table.add_row("Opportunity", str(summary.opportunity_score))
    table.add_row("Difficulty", str(summary.difficulty_score))
    table.add_row("Readiness", str(summary.data_readiness_score))
    console.print(table)


@app.callback()
def main(verbose: bool = typer.Option(False, "--verbose", help="Enable debug logging.")) -> None:
    configure_logging(verbose=verbose)


@app.command()
def bootstrap(
    force: bool = typer.Option(False, help="Reinstall even if aihubshell exists."),
) -> None:
    """Install or verify the official aihubshell without using sudo."""

    try:
        settings = _settings()
        result = install_aihubshell(settings, force=force)
    except (ConfigurationError, InstallationError) as error:
        _handle_error(error)
        return

    action = "installed" if result.installed else "verified existing"
    console.print(f"[green]aihubshell {action} at {result.path}[/green]")
    console.print(
        result.verification_output.splitlines()[0]
        if result.verification_output
        else "verification ok"
    )
    if result.path_guidance:
        console.print(f"[yellow]{result.path_guidance}[/yellow]")


@app.command()
def doctor() -> None:
    """Validate Python version, directories, shell installation, and harmless metadata access."""

    rows: list[tuple[str, str, str]] = []
    exit_code = 0

    current_python_version = ScoutSettings.current_python_version()
    python_value = ScoutSettings.format_python_version(current_python_version)
    try:
        ScoutSettings.validate_python_version(current_python_version)
        rows.append((f"Python {MINIMUM_PYTHON_LABEL}", python_value, "ok"))
    except ConfigurationError as error:
        rows.append(
            (
                f"Python {MINIMUM_PYTHON_LABEL}",
                f"{python_value} | {error}",
                "fail",
            )
        )
        exit_code = 1

    try:
        settings = _settings()
        rows.append(("Output directory", str(settings.output_dir), "ok"))
        rows.append(("Cache directory", str(settings.cache_dir), "ok"))
    except ConfigurationError as error:
        rows.append(("Configuration", str(error), "fail"))
        settings = None
        exit_code = 1

    if settings is not None:
        shell_path = resolve_shell_path(settings)
        if shell_path is None:
            rows.append(("aihubshell", "not found", "fail"))
            exit_code = 1
        else:
            rows.append(("aihubshell", str(shell_path), "ok"))
            try:
                wrapper = AIHubShellWrapper(settings)
                wrapper.verify_metadata_access()
                rows.append(("Metadata list command", "aihubshell -mode l", "ok"))
            except (ConfigurationError, ShellExecutionError) as error:
                rows.append(("Metadata list command", str(error), "fail"))
                exit_code = 1
        rows.append(
            (
                "AIHUB_API_KEY",
                "configured"
                if settings.aihub_api_key
                else "not set (optional for metadata-only flow)",
                "ok",
            )
        )

    table = Table(title="Environment Doctor")
    table.add_column("Check")
    table.add_column("Value")
    table.add_column("Status")
    for check, value, status in rows:
        style = "green" if status == "ok" else "red"
        table.add_row(check, value, f"[{style}]{status}[/{style}]")
    console.print(table)

    if exit_code:
        raise typer.Exit(code=exit_code)


@app.command("list")
def list_datasets(
    limit: int | None = typer.Option(None, min=1, help="Only print the first N rows."),
) -> None:
    """List available datasets and save normalized JSON."""

    try:
        settings = _require_runtime()
        result = run_list_datasets(settings)
    except (ConfigurationError, ShellExecutionError) as error:
        _handle_error(error)
        return

    datasets = result.datasets[:limit] if limit else result.datasets
    _print_list_table(
        [
            (item.dataset_key, item.title, item.category_guess, item.modality_guess)
            for item in datasets
        ]
    )
    console.print(f"Saved normalized listing to {result.normalized_output_path}")


@app.command()
def inspect(datasetkey: int = typer.Option(..., "--datasetkey", min=1)) -> None:
    """Inspect one dataset and save parsed JSON."""

    try:
        settings = _require_runtime()
        summary = inspect_dataset(settings, datasetkey)
    except (ConfigurationError, ShellExecutionError) as error:
        _handle_error(error)
        return

    _print_summary_table(summary)
    console.print(f"Saved normalized dataset JSON to {summary.normalized_output_path}")


@app.command()
def summarize(datasetkey: int = typer.Option(..., "--datasetkey", min=1)) -> None:
    """Inspect one dataset and generate JSON plus Markdown artifacts."""

    try:
        settings = _require_runtime()
        summary = inspect_dataset(settings, datasetkey)
        markdown_path = generate_dataset_brief(settings, summary)
    except (ConfigurationError, ShellExecutionError) as error:
        _handle_error(error)
        return

    _print_summary_table(summary)
    console.print(f"Saved JSON to {summary.normalized_output_path}")
    console.print(f"Saved Markdown brief to {markdown_path}")


@app.command()
def scan(
    limit: int = typer.Option(20, min=1, help="Maximum number of datasets to inspect."),
    refresh: bool = typer.Option(
        False, help="Re-fetch datasets even if normalized JSON already exists."
    ),
) -> None:
    """Iterate through datasets, generate artifacts, and rebuild the index."""

    try:
        settings = _require_runtime()
        listing = run_list_datasets(settings)
    except (ConfigurationError, ShellExecutionError) as error:
        _handle_error(error)
        return

    selected = listing.datasets[:limit]
    result = ScanResult(
        source_command=listing.source_command,
        collected_at=datetime.now(UTC),
        limit=limit,
        total_listed=listing.dataset_count,
        list_output_path=listing.normalized_output_path,
    )

    for entry in track(selected, description="Scanning datasets"):
        result.dataset_keys.append(entry.dataset_key)
        try:
            if not refresh:
                existing = load_existing_summary(settings, entry.dataset_key)
                if existing is not None:
                    markdown_path = generate_dataset_brief(settings, existing)
                    result.generated_markdown_files.append(str(markdown_path))
                    result.skipped += 1
                    continue
            summary = inspect_dataset(settings, entry.dataset_key, title_hint=entry.title)
            markdown_path = generate_dataset_brief(settings, summary)
            result.generated_markdown_files.append(str(markdown_path))
            result.processed += 1
        except Exception as error:  # pragma: no cover - defensive scan behavior
            logger.exception("scan failed for dataset %s", entry.dataset_key)
            result.failed += 1
            result.parse_warnings.append(f"{entry.dataset_key}: {error}")

    markdown_path, json_path = build_catalog_index(settings)
    result.catalog_output_path = str(markdown_path)
    result.catalog_json_path = str(json_path)
    scan_path = write_scan_result(settings, result)
    result.scan_output_path = path_to_str(scan_path)

    console.print(
        f"Processed={result.processed} Skipped={result.skipped} Failed={result.failed} "
        f"| scan manifest: {scan_path}"
    )
    console.print(f"Catalog Markdown: {markdown_path}")


@app.command("build-index")
def build_index() -> None:
    """Build a ranked catalog from existing normalized dataset summaries."""

    try:
        settings = _require_runtime()
        markdown_path, json_path = build_catalog_index(settings)
    except ConfigurationError as error:
        _handle_error(error)
        return

    console.print(f"Saved catalog Markdown to {markdown_path}")
    console.print(f"Saved catalog JSON to {json_path}")


if __name__ == "__main__":
    app()
