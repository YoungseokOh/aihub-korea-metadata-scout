#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

PYTHON_VERSION="${PYTHON_VERSION:-3.11}"
FORCE_SYNC="${FORCE_SYNC:-0}"
VENV_DIR="$ROOT_DIR/.venv"
VENV_PYTHON="$VENV_DIR/bin/python"
CLI_BIN="$VENV_DIR/bin/aihub-korea-scout"
SYNC_STAMP="$VENV_DIR/.run-sync-stamp"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv가 필요합니다. https://docs.astral.sh/uv/ 를 참고해 설치하세요." >&2
  exit 1
fi

if [[ "${1:-}" == "" ]]; then
  set -- --help
fi

IFS=. read -r requested_major requested_minor _ <<< "$PYTHON_VERSION"
REQUESTED_MAJOR_MINOR="${requested_major}.${requested_minor:-0}"
needs_sync=0

if [[ "$FORCE_SYNC" == "1" ]]; then
  needs_sync=1
elif [[ ! -x "$VENV_PYTHON" || ! -x "$CLI_BIN" ]]; then
  needs_sync=1
else
  current_major_minor="$("$VENV_PYTHON" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
  if [[ "$current_major_minor" != "$REQUESTED_MAJOR_MINOR" ]]; then
    needs_sync=1
  elif [[ ! -f "$SYNC_STAMP" || pyproject.toml -nt "$SYNC_STAMP" || uv.lock -nt "$SYNC_STAMP" ]]; then
    needs_sync=1
  fi
fi

if [[ "$needs_sync" == "1" ]]; then
  echo "Python 환경을 준비합니다..." >&2
  uv python install "$PYTHON_VERSION" >/dev/null
  uv sync --python "$PYTHON_VERSION" --extra dev >/dev/null
  touch "$SYNC_STAMP"
fi

exec "$CLI_BIN" "$@"
