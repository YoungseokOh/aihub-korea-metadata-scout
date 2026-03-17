# AIHub Smoke Test Skill

## Purpose

Use this skill when validating the repository end to end against the live `aihubshell` command surface.

## Safe Smoke-Test Policy

- Use a temporary output root.
- Do not overwrite committed sample artifacts under `data/`.
- Keep the smoke sequence small and deterministic where possible.

## Environment

```bash
export AIHUB_OUTPUT_DIR=/tmp/aihub-smoke/data
export AIHUB_CACHE_DIR=/tmp/aihub-smoke/data/raw
```

## Recommended Sequence

```bash
uv run aihub-korea-scout doctor
uv run aihub-korea-scout list --limit 3
uv run aihub-korea-scout inspect --datasetkey 593
uv run aihub-korea-scout summarize --datasetkey 593
uv run aihub-korea-scout build-index
uv run aihub-korea-scout scan --limit 2
```

## What To Check

- command exits are successful
- raw cache files are created
- normalized JSON files are created
- generated Markdown files are created
- no download commands are used

## Reporting

When reporting smoke-test results, include:

- commands executed
- whether they passed or failed
- generated artifact paths
- any parser warnings or unexpected behavior
