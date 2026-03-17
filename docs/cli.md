# CLI Reference

## Commands

### `bootstrap`

Install or verify the official `aihubshell` without using `sudo`.

```bash
uv run aihub-korea-scout bootstrap
```

Behavior:

- installs to `~/.local/bin/aihubshell` by default
- respects `AIHUB_SHELL_PATH` if set
- verifies installation with a harmless metadata list command

### `doctor`

Check runtime prerequisites and metadata access.

```bash
uv run aihub-korea-scout doctor
```

Checks:

- Python version
- output and cache directories
- `aihubshell` presence
- `aihubshell -mode l` execution
- `AIHUB_API_KEY` presence status

### `list`

Fetch dataset listing, save normalized JSON, and print a summary table.

```bash
uv run aihub-korea-scout list
uv run aihub-korea-scout list --limit 10
```

### `inspect`

Fetch and normalize one dataset file tree.

```bash
uv run aihub-korea-scout inspect --datasetkey 593
```

### `summarize`

Inspect one dataset and generate both JSON and Markdown outputs.

```bash
uv run aihub-korea-scout summarize --datasetkey 593
```

### `scan`

Run listing, inspect multiple datasets, generate Markdown, and rebuild the catalog.

```bash
uv run aihub-korea-scout scan --limit 20
uv run aihub-korea-scout scan --limit 20 --refresh
```

Behavior:

- uses `list` as the input set
- skips existing normalized summaries unless `--refresh` is set
- continues past per-dataset failures
- writes a scan manifest under `data/normalized/scans/`

### `build-index`

Build catalog artifacts from existing normalized dataset summaries.

```bash
uv run aihub-korea-scout build-index
```

## Recommended Command Order

1. `bootstrap`
2. `doctor`
3. `list`
4. `inspect` or `summarize`
5. `scan`
6. `build-index`

## Temporary Output Directory Pattern

For smoke tests or experiments, avoid mixing transient artifacts into the committed sample outputs.

```bash
env AIHUB_OUTPUT_DIR=/tmp/aihub-smoke/data \
    AIHUB_CACHE_DIR=/tmp/aihub-smoke/data/raw \
    uv run aihub-korea-scout summarize --datasetkey 593
```

