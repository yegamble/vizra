#!/usr/bin/env bash
# Check a deployment bundle: manifest, excludes, bind sources, renders (VZ-INSTALL-004).
set -euo pipefail
exec python3 "$(dirname "$0")/bundle.py" check "$@"
