#!/usr/bin/env bash
# VZ-OPS-008 "secrets untracked": no real environment file is tracked by git.
# Only *.env.example templates may be committed (.gitignore lines 11-16 say so;
# this makes it a check instead of a convention). Usage: [repo-dir]
set -euo pipefail
repo="${1:-.}"
bad="$(git -C "$repo" ls-files -- '*.env' '.env' '*/.env' '.env.*' '*/.env.*' \
  | grep -Ev '\.env\.example$' || true)"
if [ -n "$bad" ]; then
  echo "VIOLATION rule=tracked-secret-file: git tracks environment file(s) that"
  echo "may hold secrets; only *.env.example is committed:"
  printf '  %s\n' "$bad"
  exit 1
fi
echo "secrets-untracked: OK (no tracked .env / env/*.env file)"
