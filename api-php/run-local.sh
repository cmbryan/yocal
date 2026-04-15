#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

export YOCAL_DB_DIR="${ROOT_DIR}/db/yocal"
exec php -S 127.0.0.1:8000 -t "${ROOT_DIR}/api-php" "${ROOT_DIR}/api-php/index.php"
