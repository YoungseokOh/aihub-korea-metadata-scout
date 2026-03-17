# Smoke Tests

## Purpose

Smoke tests verify that the installed `aihubshell`, CLI entrypoint, parsing flow, artifact generation, and catalog build still work together end to end.

## Safe Execution Pattern

Always use a temporary output directory for live smoke tests.

```bash
export AIHUB_OUTPUT_DIR=/tmp/aihub-smoke/data
export AIHUB_CACHE_DIR=/tmp/aihub-smoke/data/raw
```

## Recommended Smoke Sequence

### 1. Environment checks

```bash
uv run aihub-korea-scout doctor
```

Expected:

- Python check is `ok`
- `aihubshell` is found
- metadata list command succeeds

### 2. Listing flow

```bash
uv run aihub-korea-scout list --limit 3
```

Expected outputs:

- `data/normalized/list/latest.json`
- `data/raw/list/latest.txt`

### 3. Single dataset inspection

```bash
uv run aihub-korea-scout inspect --datasetkey 593
uv run aihub-korea-scout summarize --datasetkey 593
```

Expected outputs:

- `data/raw/datasets/593.txt`
- `data/normalized/datasets/593.json`
- `data/generated/datasets/593-*.md`

### 4. Catalog rebuild

```bash
uv run aihub-korea-scout build-index
```

Expected outputs:

- `data/generated/index/dataset-catalog.md`
- `data/normalized/catalog.json`

### 5. Small scan

```bash
uv run aihub-korea-scout scan --limit 2
```

Expected outputs:

- scan manifest under `data/normalized/scans/`
- dataset briefs for scanned items
- updated catalog artifacts

## Validation Checklist

- commands exit successfully
- raw cache files are created
- normalized JSON files are created
- generated Markdown files are created
- no command path invokes dataset download modes

## Cleanup

Because the smoke run uses `/tmp/aihub-smoke`, cleanup is optional:

```bash
rm -rf /tmp/aihub-smoke
```

