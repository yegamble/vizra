#!/bin/sh
# shellcheck disable=SC2016 # mutation anchors are literal script text
# VZ-FOUND-001: each bootstrap guard goes red when removed (controlled mutation)
# and the suite is green on the real script. Exits non-zero if any mutation
# survives or the unmutated suite fails.
set -eu
root="$(cd "$(dirname "$0")/../../.." && pwd)"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
rc=0
expect_red() { # <name> <python replace old> <new> <expected failing case>
  python3 - "$root/bootstrap.sh" "$tmp/m.sh" "$2" "$3" <<'PY'
import sys
s=open(sys.argv[1]).read(); assert s.count(sys.argv[3])==1, "mutation anchor not unique"
open(sys.argv[2],'w').write(s.replace(sys.argv[3],sys.argv[4]))
PY
  if BOOTSTRAP="$tmp/m.sh" sh "$root/tests/bootstrap/bootstrap_test.sh" >"$tmp/out" 2>&1; then
    echo "SURVIVED $1"; rc=1
  elif grep -q "^FAIL $4" "$tmp/out"; then echo "RED $1 -> $(grep -c '^FAIL' "$tmp/out") failing, incl. $4"
  else echo "RED-WRONG-CASE $1"; cat "$tmp/out"; rc=1; fi
}
expect_red drop-dirty-check 'if [ -n "$(git -C "$dir" status --porcelain)" ]; then' 'if false; then' dirty-refused
expect_red drop-ref-validation '-*|*..*|*[!A-Za-z0-9_./-]*)' 'NEVER)' 'bad-ref'
expect_red drop-pin-checkout 'git -C "$dir" checkout -q --detach "$want"' ':' S2-ref-detached
expect_red always-checkout-default 'if [ "$(git -C "$dir" symbolic-ref -q --short HEAD || true)" != "$branch" ]; then' 'if true; then git -C "$dir" commit -q --allow-empty -m drift; fi; if true; then' R1-rerun-default
if sh "$root/tests/bootstrap/bootstrap_test.sh" >"$tmp/out" 2>&1; then echo "GREEN unmutated: $(tail -1 "$tmp/out")"
else echo "unmutated suite FAILED"; cat "$tmp/out"; rc=1; fi
exit $rc
