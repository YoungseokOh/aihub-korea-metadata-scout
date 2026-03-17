#!/usr/bin/env bash
set -euo pipefail

OFFICIAL_URL="https://api.aihub.or.kr/api/aihubshell.do"
TARGET="${AIHUB_SHELL_PATH:-$HOME/.local/bin/aihubshell}"
TARGET_DIR="$(dirname "$TARGET")"

if ! command -v curl >/dev/null 2>&1; then
  echo "curl is required to install aihubshell." >&2
  exit 1
fi

mkdir -p "$TARGET_DIR"
curl -fsSL "$OFFICIAL_URL" -o "$TARGET"
chmod +x "$TARGET"

if ! "$TARGET" -mode l >/dev/null 2>&1; then
  echo "aihubshell was downloaded to $TARGET but metadata verification failed." >&2
  exit 1
fi

echo "aihubshell installed at $TARGET"
case ":$PATH:" in
  *":$TARGET_DIR:"*) ;;
  *)
    echo "Note: $TARGET_DIR is not on PATH."
    echo "Add: export PATH=\"$TARGET_DIR:\$PATH\""
    ;;
esac

