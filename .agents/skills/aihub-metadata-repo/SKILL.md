# AIHub Metadata Repo Skill

## Purpose

Use this skill when working on `aihub-korea-metadata-scout`.

This repository is a metadata-only AI-Hub Korea exploration tool. Treat the official `aihubshell` as the only supported source of truth.

## Non-Negotiable Rules

- Never add dataset download commands.
- Never call `aihubshell -mode d` or package download modes.
- Never add placeholder download code.
- Do not reverse engineer undocumented APIs.
- Do not claim dataset meaning beyond title, visible metadata lines, and file tree structure.

## Repository Map

- `src/aihub_korea_metadata_scout/shell/`: official shell install, wrapper, parser
- `src/aihub_korea_metadata_scout/pipeline/`: list, inspect, summarize, catalog build
- `src/aihub_korea_metadata_scout/scoring/`: heuristic analysis only
- `src/aihub_korea_metadata_scout/storage/`: raw cache and artifact persistence
- `tests/fixtures/`: parser fixtures and sample shell outputs
- `data/`: committed deterministic sample outputs only

## Working Rules

- Keep changes typed and explicit.
- Preserve raw output caching and command traceability.
- Prefer partial parsing with warnings over brittle parsing.
- Update tests when changing parser, CLI, scoring, or output shape.
- Use temporary output directories for live smoke tests instead of writing live artifacts into repo `data/`.

## Useful Commands

```bash
uv sync --python 3.11 --extra dev
uv run ruff check .
uv run pytest
uv run aihub-korea-scout doctor
```

## Before Finishing

- run lint
- run tests
- if behavior changed, update `README.md` and relevant files under `docs/`

