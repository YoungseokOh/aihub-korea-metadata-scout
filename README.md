# aihub-korea-metadata-scout

`aihub-korea-metadata-scout` is a metadata-only exploration tool for AI-Hub Korea datasets.
It uses the official `aihubshell` to:

- browse dataset listings
- inspect per-dataset file-tree metadata
- normalize results into structured JSON
- generate concise Markdown briefs
- rank datasets for lightweight business-opportunity exploration

It is intentionally local-first and conservative. The project does **not** download datasets, does not expose download commands, and does not infer meaning beyond what is visible from the title, metadata lines, and file tree.

## Why Metadata-Only

AI-Hub datasets can be large, approval-gated, or operationally expensive to handle. For early exploration work, a solo developer often needs a fast answer to:

- what exists
- how large it looks
- what file layout is visible
- which datasets look easy or hard to use
- which datasets might support a commercial idea

This repository keeps that workflow lightweight by using only the official shell metadata interface.

## What This Project Does

- Installs or validates the official `aihubshell`
- Executes harmless metadata commands only: `-help`, `-mode l`, `-mode l -datasetkey <id>`
- Caches raw shell stdout for traceability
- Parses listing and file-tree output defensively
- Saves normalized JSON artifacts under `data/normalized/`
- Renders Korean-first Markdown dataset briefs under `data/generated/datasets/`
- Builds a ranked catalog under `data/generated/index/dataset-catalog.md`

## What This Project Does Not Do

- Download datasets
- Call `aihubshell -mode d` or package download modes
- Implement download helpers or placeholders
- Reverse engineer undocumented APIs
- Claim label quality, licensing suitability, or semantic coverage from metadata alone

## Prerequisites

- Linux or macOS shell environment
- `uv`
- `curl`
- Python 3.11+

The CLI also validates the active interpreter at runtime and exits with installation guidance when it is below Python 3.11.

If Python 3.11 is not available yet:

```bash
uv python install 3.11
```

## Quick Start

```bash
git clone https://github.com/YoungseokOh/aihub-korea-metadata-scout.git
cd aihub-korea-metadata-scout
make bootstrap
make doctor
```

`make bootstrap` will:

1. install Python 3.11 via `uv` if needed
2. create the project virtual environment
3. install dependencies
4. download the official `aihubshell` to `~/.local/bin/aihubshell` unless `AIHUB_SHELL_PATH` is set
5. verify the shell using a harmless metadata listing command

## Installation Without Make

```bash
uv python install 3.11
uv sync --python 3.11 --extra dev
./scripts/bootstrap_aihubshell.sh
uv run aihub-korea-scout doctor
```

## Environment Variables

Copy `.env.example` to `.env` if you want local overrides.

| Variable | Required | Purpose |
| --- | --- | --- |
| `AIHUB_API_KEY` | No | Passed through as `AIHUB_APIKEY` to the shell. Not required for metadata-only listing/inspection. |
| `AIHUB_SHELL_PATH` | No | Explicit path to the official `aihubshell` executable. Also used as the bootstrap install target if provided. |
| `AIHUB_OUTPUT_DIR` | No | Root artifact directory. Defaults to `./data`. |
| `AIHUB_CACHE_DIR` | No | Raw stdout cache directory. Defaults to `./data/raw`. |

## CLI Usage

```bash
uv run aihub-korea-scout bootstrap
uv run aihub-korea-scout doctor
uv run aihub-korea-scout list
uv run aihub-korea-scout inspect --datasetkey 593
uv run aihub-korea-scout summarize --datasetkey 593
uv run aihub-korea-scout scan --limit 20
uv run aihub-korea-scout build-index
```

## Output Layout

```text
data/
├─ raw/
│  ├─ list/latest.txt
│  ├─ list/latest.meta.json
│  ├─ datasets/<datasetkey>.txt
│  └─ datasets/<datasetkey>.meta.json
├─ normalized/
│  ├─ list/latest.json
│  ├─ datasets/<datasetkey>.json
│  ├─ scans/<timestamp>.json
│  └─ catalog.json
└─ generated/
   ├─ datasets/<datasetkey>-<slug>.md
   └─ index/dataset-catalog.md
```

## Parser Caveats

- `aihubshell` output includes banners, notices, mixed Korean/English text, and box-drawing tree characters.
- The parser prefers partial structured output over failure.
- Unknown or ambiguous lines are preserved as parse warnings.
- For missing dataset pages, the tool records the raw output and returns `parse_status=error`.
- File size totals only reflect sizes visible in the shell output.

## Scoring Caveats

- Scores are heuristic and intentionally low-precision.
- Opportunity, difficulty, and readiness are based on title, visible tree structure, apparent file fragmentation, and visible labels/splits.
- Generated summaries explicitly note when they are inferred from title and file tree only.
- Licensing, approval, privacy, and policy suitability must be validated separately.

## Development Workflow

```bash
make bootstrap
make doctor
make test
make scan
```

Useful direct commands:

```bash
uv run ruff check .
uv run ruff format .
uv run pytest
```

## Sample Outputs

Committed mocked artifacts are included for inspection:

- `data/normalized/datasets/86.json`
- `data/normalized/datasets/88.json`
- `data/generated/datasets/86-감성대화.md`
- `data/generated/datasets/88-공공행정문서-ocr.md`
- `data/generated/index/dataset-catalog.md`

These samples are derived from fixed test fixtures rather than live scans, so they stay deterministic.

## Architecture Notes

- `shell/`: installation, subprocess invocation, and defensive parsing
- `pipeline/`: list, inspect, Markdown generation, and catalog building
- `storage/`: raw cache, JSON persistence, Markdown persistence
- `scoring/`: conservative heuristics and business-opportunity analysis
- `cli.py`: Typer-based command surface

The architecture is intentionally simple: one shell boundary, one parser boundary, one normalized artifact format, and one reporting layer.
