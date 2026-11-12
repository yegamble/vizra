#!/usr/bin/env bash
# Build vizra-bundle_<tag>.tar.gz reproducibly (VZ-INSTALL-004). See scripts/bundle.py.
set -euo pipefail
exec python3 "$(dirname "$0")/bundle.py" build "$@"
