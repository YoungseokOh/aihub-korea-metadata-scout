#!/usr/bin/env bash
set -euo pipefail

PYTHON_VERSION="${PYTHON_VERSION:-3.11}"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv가 필요합니다. https://docs.astral.sh/uv/ 를 참고해 설치하세요." >&2
  exit 1
fi

if [[ "${1:-}" == "" ]]; then
  set -- --help
fi

uv python install "$PYTHON_VERSION" >/dev/null
uv sync --python "$PYTHON_VERSION" --extra dev >/dev/null

exec uv run aihub-korea-scout "$@"

