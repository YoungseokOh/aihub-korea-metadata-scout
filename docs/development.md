# Development Guide

## Local Setup

```bash
uv python install 3.11
uv sync --python 3.11 --extra dev
./scripts/bootstrap_aihubshell.sh
uv run aihub-korea-scout doctor
```

## Common Commands

```bash
make bootstrap
make doctor
make test
make scan
uv run ruff check .
uv run pytest
```

## Repository Expectations

- keep the project metadata-only
- do not add download commands or placeholders
- keep `aihubshell` as the source of truth
- preserve committed generated Markdown outputs unless intentionally regenerating them
- prefer typed, explicit, maintainable code

## When Changing Parsers

1. add or update realistic fixtures
2. update parser tests first
3. verify normalized JSON shape still makes sense
4. confirm generated Markdown stays readable

## When Changing CLI Behavior

1. update Typer command help
2. update CLI tests
3. update root README and `docs/cli.md`
4. run smoke tests with a temporary output directory

## Test Strategy

The repository uses two levels of verification.

### Fast tests

- parser unit tests
- model tests
- scoring tests
- markdown rendering tests
- CLI tests with mocks

### Smoke tests

- live `aihubshell` doctor check
- live `list`
- live `inspect` or `summarize`
- live `scan` against a small limit

Smoke tests should use `/tmp` output paths to avoid changing committed generated Markdown artifacts.
