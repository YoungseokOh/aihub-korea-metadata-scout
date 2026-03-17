# Data Artifacts

## Artifact Categories

The repository uses three artifact layers.

### Raw cache

`data/raw/`

- stores unmodified stdout from `aihubshell`
- stores command trace metadata in sidecar JSON files
- serves as the parser debugging source of truth

Typical files:

- `data/raw/list/latest.txt`
- `data/raw/list/latest.meta.json`
- `data/raw/datasets/<datasetkey>.txt`
- `data/raw/datasets/<datasetkey>.meta.json`

### Normalized JSON

`data/normalized/`

- stores typed and structured representations of listing and dataset outputs
- is the input layer for catalog building
- is suitable for downstream automation

Typical files:

- `data/normalized/list/latest.json`
- `data/normalized/datasets/<datasetkey>.json`
- `data/normalized/scans/<timestamp>.json`
- `data/normalized/catalog.json`

### Generated Markdown

`data/generated/`

- stores human-readable dataset briefs
- stores the ranked catalog view

Typical files:

- `data/generated/datasets/<datasetkey>-<slug>.md`
- `data/generated/index/dataset-catalog.md`

## Path Rules

- raw listing cache always uses `latest.txt`
- normalized listing cache always uses `latest.json`
- dataset JSON uses the exact numeric dataset key as filename
- dataset Markdown uses `<datasetkey>-<slug>.md`
- scans use UTC timestamps in the filename

## Committed vs Temporary Artifacts

The repository commits only deterministic sample artifacts derived from test fixtures.

Use a temporary output root for:

- smoke tests
- live experimentation
- one-off scans

Recommended pattern:

```bash
env AIHUB_OUTPUT_DIR=/tmp/aihub-smoke/data \
    AIHUB_CACHE_DIR=/tmp/aihub-smoke/data/raw \
    uv run aihub-korea-scout scan --limit 5
```

