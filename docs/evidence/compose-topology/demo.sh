#!/usr/bin/env bash
#
# Red/green demonstrations for the compose topology guards (VZ-ISSUE-002).
#
# Every guard in this slice is shown FAILING against a controlled mutation and
# passing once the mutation is reverted. A guard nobody has seen fail is a guard
# nobody knows still works.
#
# WHY THE DIGESTS. Each case prints the sha256 of the file it edits before and
# after the mutation, and REFUSES TO CONTINUE if they are equal. Without that, a
# mutation that silently failed to apply — a changed anchor, a moved line, a sed
# that matched nothing — would run the checker against the unmodified tree, see
# it pass, and be recorded as "the guard caught it and then went green again".
# It would not have caught anything. The digest pair is what makes the green
# half mean something.
#
# Run it from the repository root:
#     bash docs/evidence/compose-topology/demo.sh 2>&1 | tee /tmp/demo.txt
#
# It restores every file it touches, including on failure (trap), and it fails
# loudly if a restore did not land.

set -uo pipefail

cd "$(dirname "$0")/../../.." || exit 2
ROOT="$PWD"
MODELS="build/compose-models"
PASSED=0
FAILED=0
BACKUP_DIR="$(mktemp -d)"

digest() { shasum -a 256 "$1" 2>/dev/null | cut -d' ' -f1 || sha256sum "$1" | cut -d' ' -f1; }

backup() { mkdir -p "$BACKUP_DIR/$(dirname "$1")"; cp "$ROOT/$1" "$BACKUP_DIR/$1"; }
restore() { cp "$BACKUP_DIR/$1" "$ROOT/$1"; }

cleanup() {
  if [ -d "$BACKUP_DIR" ]; then
    (cd "$BACKUP_DIR" && find . -type f -print0) | while IFS= read -r -d '' f; do
      cp "$BACKUP_DIR/${f#./}" "$ROOT/${f#./}"
    done
    rm -rf "$BACKUP_DIR"
  fi
}
trap cleanup EXIT

# Apply a mutation to $1 using the python snippet on stdin, proving the file
# actually changed.
mutate() {
  local file="$1" before after
  backup "$file"
  before="$(digest "$file")"
  python3 - "$file" || return 2
  after="$(digest "$file")"
  echo "    digest before: $before"
  echo "    digest after : $after"
  if [ "$before" = "$after" ]; then
    echo "    !! THE MUTATION DID NOT APPLY. The file is byte-identical, so anything"
    echo "       green below would be green about the UNMUTATED tree. Aborting this case."
    FAILED=$((FAILED + 1))
    return 2
  fi
  return 0
}

revert() {
  local file="$1" before after
  before="$(digest "$file")"
  restore "$file"
  after="$(digest "$file")"
  echo "    digest restored: $after"
  if [ "$before" = "$after" ]; then
    echo "    !! THE RESTORE DID NOT CHANGE THE FILE."
    FAILED=$((FAILED + 1))
    return 2
  fi
}

# Render, then run a checker; expect exit $2 and, when given, the rule in $3.
expect() {
  local label="$1" want_rc="$2" want_rule="${3:-}" out rc
  out="$( { ./scripts/compose-render.py --all --out "$MODELS" \
              && ./scripts/check-compose-topology.py "$MODELS" \
              && ./scripts/check-config-coverage.py "$MODELS"; } 2>&1 )"
  rc=$?
  if [ "$rc" != "$want_rc" ]; then
    echo "    FAIL: expected exit $want_rc, got $rc"
    printf '%s\n' "$out" | sed 's/^/      | /' | head -12
    FAILED=$((FAILED + 1)); return 1
  fi
  if [ -n "$want_rule" ] && ! printf '%s\n' "$out" | grep -qF "$want_rule"; then
    echo "    FAIL: exit $rc was right but the expected signal was absent:"
    echo "          wanted: $want_rule"
    printf '%s\n' "$out" | grep -E 'VIOLATION|FAILED|UNEVALUABLE' | sed 's/^/      | /' | head -8
    FAILED=$((FAILED + 1)); return 1
  fi
  echo "    ok  ($label: exit $rc${want_rule:+, signal \"$want_rule\"})"
  printf '%s\n' "$out" | grep -E 'VIOLATION|FAILED TO RENDER|UNEVALUABLE|is not a valid DSN|is empty, but' \
    | sed 's/^/      | /' | head -4
  PASSED=$((PASSED + 1)); return 0
}

case_header() { echo; echo "=============================================================="; echo "CASE $1"; echo "=============================================================="; }

echo "vizra compose-topology red/green demonstrations"
echo "date:  $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "tree:  $(git rev-parse HEAD 2>/dev/null || echo '(not a git tree)')"
echo "dirty: $(git status --porcelain 2>/dev/null | wc -l | tr -d ' ') file(s)"
echo "docker compose: $(docker compose version --short)"
echo "python: $(python3 --version 2>&1)"

case_header "0 — BASELINE: the unmutated tree is green"
expect "baseline" 0

# ---------------------------------------------------------------------------
case_header "1 — a ports: entry on postgres in the BASE file"
mutate docker-compose.yml <<'PY' && {
import sys, io
p = sys.argv[1]
s = open(p).read()
anchor = "  postgres:\n"
s = s.replace(anchor, anchor + '    ports:\n      - "5432:5432"\n', 1)
open(p, "w").write(s)
PY
  expect "postgres publishes in the base file" 1 "rule=never-published service=postgres"
  revert docker-compose.yml
  expect "restored" 0
}

# ---------------------------------------------------------------------------
case_header "2 — a ports: entry on the CACHE in an OVERLAY (docker-compose.prod.yml)"
mutate docker-compose.prod.yml <<'PY' && {
import sys
p = sys.argv[1]
s = open(p).read()
anchor = "  redis:\n    restart: unless-stopped\n"
s = s.replace(anchor, anchor + '    ports:\n      - "6379:6379"\n', 1)
open(p, "w").write(s)
PY
  expect "the cache publishes from an overlay" 1 "rule=never-published service=redis"
  revert docker-compose.prod.yml
  expect "restored" 0
}

# ---------------------------------------------------------------------------
case_header "3 — a ports: entry on SEARCH in the BASE file"
mutate docker-compose.yml <<'PY' && {
import sys
p = sys.argv[1]
s = open(p).read()
anchor = '    profiles: ["search"]\n'
s = s.replace(anchor, anchor + '    ports:\n      - "8081:8081"\n', 1)
open(p, "w").write(s)
PY
  expect "search publishes" 1 "rule=never-published service=search"
  revert docker-compose.yml
  expect "restored" 0
}

# ---------------------------------------------------------------------------
case_header "4 — api bound to 0.0.0.0 instead of 127.0.0.1"
mutate docker-compose.prod.yml <<'PY' && {
import sys
p = sys.argv[1]
s = open(p).read()
s = s.replace('- !override "127.0.0.1:${VIZRA_HTTP_PORT:-8080}:8080"',
              '- !override "0.0.0.0:${VIZRA_HTTP_PORT:-8080}:8080"', 1)
open(p, "w").write(s)
PY
  expect "api faces the network" 1 "rule=public-bind service=api"
  revert docker-compose.prod.yml
  expect "restored" 0
}

# ---------------------------------------------------------------------------
case_header "5 — caddy present OUTSIDE the edge profile"
mutate docker-compose.yml <<'PY' && {
import sys
p = sys.argv[1]
s = open(p).read()
s = s.replace('    profiles: ["edge"]\n', '    profiles: ["core"]\n', 1)
open(p, "w").write(s)
PY
  expect "caddy escapes the edge profile" 1 "rule=edge-profile service=caddy"
  revert docker-compose.yml
  expect "restored" 0
}

# ---------------------------------------------------------------------------
case_header "6a — a long-running service with NO restart policy"
mutate docker-compose.yml <<'PY' && {
import sys
p = sys.argv[1]
s = open(p).read()
anchor = "  frontend:\n    image: ${VIZRA_IMAGE_REGISTRY:-ghcr.io}/${VIZRA_IMAGE_OWNER:-yegamble}/vizra-user:${VIZRA_USER_TAG:-dev}\n    profiles: [\"frontend\"]\n    restart: unless-stopped\n"
assert anchor in s, "anchor not found"
s = s.replace(anchor, anchor.replace("    restart: unless-stopped\n", ""), 1)
open(p, "w").write(s)
PY
  expect "frontend would not survive a reboot" 1 "rule=missing-restart service=frontend"
  revert docker-compose.yml
  expect "restored" 0
}

case_header "6b — a service with NO log cap"
mutate docker-compose.yml <<'PY' && {
import sys
p = sys.argv[1]
s = open(p).read()
anchor = '    profiles: ["analytics"]\n    restart: unless-stopped\n    logging: *logging\n'
assert anchor in s, "anchor not found"
s = s.replace(anchor, '    profiles: ["analytics"]\n    restart: unless-stopped\n', 1)
open(p, "w").write(s)
PY
  expect "clickhouse logs are unbounded" 1 "rule=missing-log-cap service=clickhouse"
  revert docker-compose.yml
  expect "restored" 0
}

case_header "6c — a long-running service with NO healthcheck"
mutate docker-compose.yml <<'PY' && {
import sys, re
p = sys.argv[1]
s = open(p).read()
anchor = '''    healthcheck:
      test: ["CMD", "valkey-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 10
      start_period: 5s
'''
assert anchor in s, "anchor not found"
s = s.replace(anchor, "", 1)
open(p, "w").write(s)
PY
  expect "the cache cannot gate a depends_on" 1 "rule=missing-healthcheck service=redis"
  revert docker-compose.yml
  expect "restored" 0
}

# ---------------------------------------------------------------------------
case_header "7 — build: on the migration one-shot in a PRODUCTION shape"
mutate docker-compose.prod.yml <<'PY' && {
import sys
p = sys.argv[1]
s = open(p).read()
# NOTE: simply DELETING `build: !reset null` proves nothing - the base file
# carries no build: at all (it lives only in docker-compose.dev.yml, which the
# production chain never loads), so the rendered production model is unchanged.
# The failure being modelled is an overlay that REINTRODUCES a build on the
# one-shot, which is what `compose run` would then compile on the host.
s = s.replace("    build: !reset null\n    restart: \"no\"\n",
              "    build:\n      context: ./vizra-core\n    restart: \"no\"\n", 1)
open(p, "w").write(s)
PY
  expect "the one-shot would compile on the host" 1 "rule=production-build service=migrate"
  revert docker-compose.prod.yml
  expect "restored" 0
}

# ---------------------------------------------------------------------------
case_header "8a — an image tagged :latest in a production shape"
mutate docker-compose.prod.yml <<'PY' && {
import sys, re
p = sys.argv[1]
s = open(p).read()
old = "  frontend:\n    image: ${VIZRA_IMAGE_REGISTRY:-ghcr.io}/${VIZRA_IMAGE_OWNER:-yegamble}/vizra-user:${VIZRA_USER_TAG:?"
i = s.index(old)
j = s.index("\n", s.index("image:", i))
s = s[:s.index("image:", i)] + "image: ghcr.io/yegamble/vizra-user:latest" + s[j:]
open(p, "w").write(s)
PY
  expect "frontend runs :latest" 1 "rule=unpinned-image service=frontend"
  revert docker-compose.prod.yml
  expect "restored" 0
}

case_header "8b — an UNTAGGED image in a production shape"
mutate docker-compose.prod.yml <<'PY' && {
import sys
p = sys.argv[1]
s = open(p).read()
old = "  frontend:\n    image: ${VIZRA_IMAGE_REGISTRY:-ghcr.io}/${VIZRA_IMAGE_OWNER:-yegamble}/vizra-user:${VIZRA_USER_TAG:?"
i = s.index(old)
j = s.index("\n", s.index("image:", i))
s = s[:s.index("image:", i)] + "image: ghcr.io/yegamble/vizra-user" + s[j:]
open(p, "w").write(s)
PY
  expect "frontend has no tag, which Docker resolves to :latest" 1 "rule=unpinned-image service=frontend"
  revert docker-compose.prod.yml
  expect "restored" 0
}

# ---------------------------------------------------------------------------
case_header "9a — a config key added to a component registry with NO template entry"
mutate env/registry/core.json <<'PY' && {
import sys, json
p = sys.argv[1]
d = json.load(open(p))
d["keys"].append({"name": "VIZRA_BRAND_NEW_KEY", "required": "optional",
                  "secret": False, "delivered_by": "template"})
json.dump(d, open(p, "w"), indent=2); open(p, "a").write("\n")
PY
  expect "core declares a key nothing delivers" 1 "rule=service-key-missing"
  revert env/registry/core.json
  expect "restored" 0
}

case_header "9b — a template key with NO consumer (the reverse direction)"
mutate env/production.env.example <<'PY' && {
import sys
p = sys.argv[1]
s = open(p).read()
open(p, "w").write(s + "\nVIZRA_KEY_NOBODY_READS=something\n")
PY
  expect "a template key reaches no process" 1 "rule=template-key-unused"
  revert env/production.env.example
  expect "restored" 0
}

# ---------------------------------------------------------------------------
case_header "10a — an INVALID external DSN"
echo "    (no file is mutated: the DSN is supplied through the environment,"
echo "     exactly as an operator's env file supplies it)"
out="$(DATABASE_URL='hunter2' ./scripts/compose-render.py --shape prod-external-postgres --out "$MODELS" 2>&1)"; rc=$?
if [ "$rc" = "1" ] && printf '%s\n' "$out" | grep -q 'DATABASE_URL is not a valid DSN'; then
  if printf '%s\n' "$out" | grep -q 'hunter2'; then
    echo "    FAIL: the message ECHOED the value. A DSN carries a password."
    FAILED=$((FAILED + 1))
  else
    echo "    ok  (exit 1, names the variable, does not echo the value)"
    printf '%s\n' "$out" | sed 's/^/      | /'
    PASSED=$((PASSED + 1))
  fi
else
  echo "    FAIL: expected exit 1 with an actionable message, got $rc"
  printf '%s\n' "$out" | sed 's/^/      | /'
  FAILED=$((FAILED + 1))
fi

case_header "10b — a MISSING external DSN"
out="$(DATABASE_URL='' ./scripts/compose-render.py --shape prod-external-postgres --out "$MODELS" 2>&1)"; rc=$?
if [ "$rc" = "1" ] && printf '%s\n' "$out" | grep -q 'DATABASE_URL is empty'; then
  echo "    ok  (exit 1, names the variable and the overlay that requires it)"
  printf '%s\n' "$out" | sed 's/^/      | /'
  PASSED=$((PASSED + 1))
else
  echo "    FAIL: expected exit 1, got $rc"; printf '%s\n' "$out" | sed 's/^/      | /'
  FAILED=$((FAILED + 1))
fi

# ---------------------------------------------------------------------------
case_header "11 — a production shape rendered with the component checkouts ABSENT (expects GREEN)"
out="$(./scripts/compose-render.py --shape bundle-no-checkouts --out "$MODELS" 2>&1)"; rc=$?
if [ "$rc" = "0" ]; then
  echo "    ok  (exit 0 - rendered from a tree containing no vizra-core, vizra-user or vizra-search)"
  printf '%s\n' "$out" | sed 's/^/      | /'
  PASSED=$((PASSED + 1))
else
  echo "    FAIL: expected exit 0, got $rc"; printf '%s\n' "$out" | sed 's/^/      | /'
  FAILED=$((FAILED + 1))
fi

# ---------------------------------------------------------------------------
case_header "12 — a SHAPE REMOVED from the lane's list"
mutate scripts/compose-shapes.json <<'PY' && {
import sys, json
p = sys.argv[1]
d = json.load(open(p))
d["shapes"] = [s for s in d["shapes"] if s["id"] != "prod-external-postgres"]
json.dump(d, open(p, "w"), indent=2); open(p, "a").write("\n")
PY
  out="$(./scripts/compose-render.py --all --out "$MODELS" 2>&1)"; rc=$?
  if [ "$rc" = "1" ] && printf '%s\n' "$out" | grep -q "SHAPE FLOOR VIOLATION"; then
    echo "    ok  (exit 1 - the floor refuses a smaller matrix)"
    printf '%s\n' "$out" | sed 's/^/      | /' | head -6
    PASSED=$((PASSED + 1))
  else
    echo "    FAIL: expected exit 1 with a floor violation, got $rc"
    printf '%s\n' "$out" | sed 's/^/      | /' | head -6
    FAILED=$((FAILED + 1))
  fi
  revert scripts/compose-shapes.json
  expect "restored" 0
}

# ---------------------------------------------------------------------------
echo
echo "=============================================================="
echo "RESULT: $PASSED assertion(s) passed, $FAILED failed"
echo "final tree digest check:"
git status --porcelain | sed 's/^/  /'
if [ -n "$(git status --porcelain)" ]; then
  echo "  !! the tree is not clean; a restore did not land"
  exit 1
fi
echo "  tree is clean - every mutation was reverted"
[ "$FAILED" = "0" ] || exit 1
