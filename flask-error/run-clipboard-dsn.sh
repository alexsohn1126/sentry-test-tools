#!/usr/bin/env bash
set -euo pipefail

if ! command -v pbpaste >/dev/null 2>&1; then
  echo "pbpaste not found (this script expects macOS clipboard)." >&2
  exit 1
fi

DSN="$(pbpaste | tr -d '[:space:]')"

if [[ ! "$DSN" =~ ^https?://[^@]+@[^/]+/[0-9]+$ ]]; then
  echo "Clipboard does not look like a Sentry DSN:" >&2
  echo "  $DSN" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# shellcheck disable=SC1091
source .venv/bin/activate

export SENTRY_DSN="$DSN"
echo "Starting flask-error with DSN from clipboard: $SENTRY_DSN"
exec python app.py
