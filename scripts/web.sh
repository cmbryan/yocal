#!/usr/bin/env bash
# Launch the chanting-stand web UI (yocal_service.app).
# Usage: scripts/web.sh [port]        HOST=0.0.0.0 scripts/web.sh   (expose on LAN)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PORT="${1:-${PORT:-5055}}"
HOST="${HOST:-127.0.0.1}"

cd "$ROOT"
if [[ -x .venv/bin/python ]]; then
    PY=.venv/bin/python
else
    PY=python3
fi

echo "yocal web UI: http://${HOST}:${PORT}/"
exec "$PY" -m flask --app yocal_service.app run --host "$HOST" --port "$PORT"
