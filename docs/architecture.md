# Architecture

## Goal

`aihub-korea-metadata-scout` is a metadata-only exploration tool for AI-Hub Korea datasets.
It deliberately stays on the safe side of the official `aihubshell` surface:

- `-help`
- `-mode l`
- `-mode l -datasetkey <id>`

It does not download datasets and does not wrap download flows.

## Main Runtime Flow

1. Resolve configuration from environment variables and defaults.
2. Resolve or install the official `aihubshell`.
3. Execute `aihubshell` via `subprocess`.
4. Cache raw stdout for traceability.
5. Parse the shell output into typed Pydantic models.
6. Enrich the parsed data with conservative heuristics.
7. Persist normalized JSON and generated Markdown artifacts.

## Package Layout

### `shell/`

- `install.py`: downloads and verifies the official `aihubshell`
- `wrapper.py`: subprocess execution and command trace capture
- `parser.py`: defensive parsing for list output and per-dataset tree output

This package is the only boundary that touches the external shell.

### `pipeline/`

- `list_datasets.py`: listing fetch + parse + persistence
- `inspect_dataset.py`: single-dataset inspection + analysis + JSON persistence
- `generate_markdown.py`: dataset brief rendering
- `build_catalog.py`: cross-dataset Markdown and JSON index generation

The pipeline modules keep orchestration simple and explicit.

### `storage/`

- `cache.py`: raw stdout cache and sidecar trace metadata
- `json_store.py`: normalized JSON read/write helpers
- `markdown_store.py`: Markdown path and write helpers

These modules centralize artifact paths and persistence behavior.

### `scoring/`

- `heuristics.py`: category/modality guesses and plain-language dataset summary
- `business_analysis.py`: lightweight business opportunity, difficulty, and readiness analysis

Scoring is heuristic by design. It is intended for exploration, not authoritative evaluation.

### `cli.py`

Typer-based command entrypoint. CLI behavior is intentionally thin and delegates almost everything to the pipeline modules.

## Design Constraints

- Metadata only
- Official `aihubshell` only
- Strong typing and explicit uncertainty
- Prefer partial parse results over hard failure
- Deterministic output paths where practical
- Simple maintainable code over abstraction-heavy architecture

## Important Decisions

### Raw output is preserved

Every shell call caches raw stdout and a sidecar command trace. This makes parser regressions debuggable and keeps normalization auditable.

### Parsing is best-effort

Mixed banners, Korean notices, and box-drawing file trees are common in `aihubshell` output. The parser extracts structured data where possible and stores warnings for anything ambiguous.

### Scoring stays explainable

Business and practicality analysis is based only on visible metadata, file paths, apparent size, and apparent structure. Every score has reasons and avoids fake precision.

