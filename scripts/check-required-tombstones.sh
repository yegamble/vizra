#!/usr/bin/env bash
#
# Lane-retirement rule for .github/required-checks.txt (VZ-CI-001 S1).
#
# Compares the manifest under test with the manifest on the BASE commit. A lane
# listed in the base may leave the head manifest only if the head carries
#     # tombstone: <lane> retired <YYYY-MM-DD> because <reason>
# Rejected: removal or commenting-out without a tombstone; a malformed
# tombstone (no/invalid date, no reason); a tombstone for a lane the base never
# had, for a lane still listed, or for a floor lane; deleting an earlier
# tombstone. The base comes from git — pull_request.base.sha, then
# merge_group.base_sha, else the merge base with origin/main — and the check
# FAILS CLOSED when it cannot be read.
#
# usage: check-required-tombstones.sh [--base-file F --head-file F]
set -uo pipefail

manifest=".github/required-checks.txt"
floor="validate"
base_file=""; head_file="$manifest"
while [ $# -gt 0 ]; do
  case "$1" in
    --base-file) base_file="$2"; shift 2 ;;
    --head-file) head_file="$2"; shift 2 ;;
    *) echo "unknown argument: $1"; exit 2 ;;
  esac
done

tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
unavailable() {
  echo "BASE MANIFEST UNAVAILABLE: $1"
  echo "  Without the base manifest a removed lane cannot be detected; failing closed."
  exit 1
}

if [ -z "$base_file" ]; then
  sha="${BASE_SHA:-}"
  if [ -z "$sha" ] && [ -n "${GITHUB_EVENT_PATH:-}" ] && [ -r "$GITHUB_EVENT_PATH" ]; then
    sha="$(python3 -c 'import json,sys; e=json.load(open(sys.argv[1])); print((e.get("pull_request") or {}).get("base",{}).get("sha") or (e.get("merge_group") or {}).get("base_sha") or "")' "$GITHUB_EVENT_PATH" 2>/dev/null || true)"
  fi
  if [ -z "$sha" ]; then
    sha="$(git merge-base HEAD origin/main 2>/dev/null || true)"
  fi
  [ -n "$sha" ] || unavailable "no base SHA (no event payload, no merge base with origin/main)"
  printf '%s' "$sha" | grep -qE '^[0-9a-f]{40}$' || unavailable "base '$sha' is not a 40-hex SHA"
  if ! git cat-file -e "$sha^{commit}" 2>/dev/null; then
    git fetch --no-tags --depth=1 origin "$sha" >/dev/null 2>&1 || true
  fi
  git show "$sha:$manifest" > "$tmp/base" 2>/dev/null || unavailable "cannot read $manifest at $sha"
  base_file="$tmp/base"
  echo "base manifest: $manifest at $sha"
fi
[ -r "$base_file" ] || unavailable "cannot read $base_file"
[ -r "$head_file" ] || { echo "HEAD MANIFEST UNREADABLE: $head_file"; exit 1; }

lanes() { grep -vE '^[[:space:]]*(#|$)' "$1" | tr -d '\r' | sed 's/[[:space:]]*$//' || true; }
stones() { tr -d '\r' < "$1" | grep -iE '^[[:space:]]*#[[:space:]]*tombstone' || true; }
valid_re='^# tombstone: ([a-z0-9][a-z0-9-]*) retired ([0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])) because [^[:space:]].*$'
stone_lane() { sed -E 's/^# tombstone: ([a-z0-9-]+) .*/\1/'; }

lanes "$base_file" > "$tmp/bl"; lanes "$head_file" > "$tmp/hl"
stones "$base_file" > "$tmp/bs"; stones "$head_file" > "$tmp/hs"
bad=0

while IFS= read -r s; do
  [ -z "$s" ] && continue
  if ! printf '%s\n' "$s" | grep -qE "$valid_re"; then
    echo "MALFORMED TOMBSTONE: '$s'"
    echo "  required: # tombstone: <lane> retired <YYYY-MM-DD> because <reason>"
    bad=1; continue
  fi
  l="$(printf '%s\n' "$s" | stone_lane)"
  if printf '%s\n' "$floor" | grep -qxF "$l"; then
    echo "FLOOR LANE: $l cannot be retired by tombstone"; bad=1
  fi
  if grep -qxF "$l" "$tmp/hl"; then
    echo "STILL LISTED: $l has a tombstone but is still in the manifest"; bad=1
  fi
  if ! grep -qxF "$l" "$tmp/bl" && ! grep -qE "^# tombstone: $l " "$tmp/bs"; then
    echo "BASE NEVER HAD: $l is tombstoned but the base manifest never listed it"; bad=1
  fi
done < "$tmp/hs"

while IFS= read -r s; do
  [ -z "$s" ] && continue
  if ! grep -qxF "$s" "$tmp/hs"; then
    echo "TOMBSTONE DELETED: $(printf '%s\n' "$s" | stone_lane) — an earlier tombstone must stay verbatim: '$s'"; bad=1
  fi
done < "$tmp/bs"

while IFS= read -r l; do
  [ -z "$l" ] && continue
  grep -qxF "$l" "$tmp/hl" && continue
  if ! grep -E "$valid_re" "$tmp/hs" | grep -qE "^# tombstone: $l "; then
    echo "REMOVED WITHOUT TOMBSTONE: $l was required on the base and is gone from $manifest"
    echo "  Retire a lane with: # tombstone: $l retired <YYYY-MM-DD> because <reason>"
    bad=1
  fi
done < "$tmp/bl"

[ "$bad" = 0 ] || exit 1
echo "tombstones: every lane removed since the base is retired by a valid tombstone"
