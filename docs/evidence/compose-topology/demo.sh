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
#
# WHY HERE-STRINGS AND NOT `printf … | grep`. Every test below reads its
# captured output with `grep … <<< "$out"`, and no reporting pipeline ends in
# `head`. Both used to, and under `set -o pipefail` that is a race: `grep -q`
# exits at its first match and closes the pipe, `printf` then takes EPIPE, and
# pipefail propagates that non-zero through a pipeline whose grep MATCHED. The
# `if` takes the else branch and the case reports `FAIL: expected exit 1 …,
# got 1` — a required lane going red with no product cause, sending whoever
# reads it hunting a regression that does not exist. The verifier hit it once in
# a clean run at 9c4b5d3 (72/73) and could not reproduce it in isolation; it
# fires under load, which a full run provides. A here-string is a file
# descriptor, not a process, so there is no producer to signal. `head -N` is
# gone for the same reason: it closes the pipe early on whatever feeds it.
# Do not "simplify" either back.
#
# The fix must not make a condition unconditionally true, and does not: an
# absent signal still returns 1 from `grep -qF`, so a genuinely broken guard is
# still reported FAIL. That is demonstrated in the committed transcript.

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
              && ./scripts/check-config-coverage.py "$MODELS" \
              && ./scripts/check-template-claims.py \
              && ./scripts/check-doc-links.py; } 2>&1 )"
  rc=$?
  if [ "$rc" != "$want_rc" ]; then
    echo "    FAIL: expected exit $want_rc, got $rc"
    sed -n '1,12p' <<< "$out" | sed 's/^/      | /'
    FAILED=$((FAILED + 1)); return 1
  fi
  if [ -n "$want_rule" ] && ! grep -qF "$want_rule" <<< "$out"; then
    echo "    FAIL: exit $rc was right but the expected signal was absent:"
    echo "          wanted: $want_rule"
    grep -E 'VIOLATION|FAILED|UNEVALUABLE' <<< "$out" | sed -n '1,8p' | sed 's/^/      | /'
    FAILED=$((FAILED + 1)); return 1
  fi
  echo "    ok  ($label: exit $rc${want_rule:+, signal \"$want_rule\"})"
  grep -E 'VIOLATION|FAILED TO RENDER|UNEVALUABLE|is not a valid DSN|is empty, but' <<< "$out" \
    | sed -n '1,4p' | sed 's/^/      | /'
  PASSED=$((PASSED + 1)); return 0
}

CASES=0
case_header() { CASES=$((CASES + 1)); echo; echo "=============================================================="; echo "CASE $1"; echo "=============================================================="; }

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

case_header "6d (V2) — a healthcheck DISABLED with disable: true"
mutate docker-compose.yml <<'PY' && {
import sys
p = sys.argv[1]
s = open(p).read()
old = '      test: ["CMD", "valkey-cli", "ping"]\n'
new = '      disable: true\n' + old
assert old in s, "anchor not found"
open(p, "w").write(s.replace(old, new, 1))
PY
  expect "disable: true is a disabled probe" 1 "rule=missing-healthcheck service=redis"
  revert docker-compose.yml
  expect "restored" 0
}

case_header "6e (V2) — a healthcheck DISABLED with Docker's test: [NONE]"
echo "    (a one-element list is not falsy, so this spelling used to PASS the rule"
echo "     that its neighbour disable: true already failed)"
mutate docker-compose.yml <<'PY' && {
import sys
p = sys.argv[1]
s = open(p).read()
old = '      test: ["CMD", "valkey-cli", "ping"]'
assert old in s, "anchor not found"
open(p, "w").write(s.replace(old, '      test: ["NONE"]', 1))
PY
  expect "test: [NONE] is Docker's spelling of disabled" 1 "rule=missing-healthcheck service=redis"
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

case_header "8c (V4) — a THIRD-PARTY image demoted from its digest to a bare tag"
echo "    (ADR-001 pins PostgreSQL and Valkey by digest; a bare tag is a moving"
echo "     target, so a rollback does not roll the datastore image back)"
mutate docker-compose.yml <<'PY' && {
import sys
p = sys.argv[1]
s = open(p).read()
old = "image: postgres:18@sha256:86c951e05bf56c93d95d397747fb8820ac76cc3bedb78f43abd83eedbe3666ae"
assert old in s, "anchor not found"
open(p, "w").write(s.replace(old, "image: postgres:18", 1))
PY
  expect "postgres lost its digest pin" 1 "rule=unpinned-image service=postgres"
  revert docker-compose.yml
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
if [ "$rc" = "1" ] && grep -q 'DATABASE_URL is not a valid DSN' <<< "$out"; then
  if grep -q 'hunter2' <<< "$out"; then
    echo "    FAIL: the message ECHOED the value. A DSN carries a password."
    FAILED=$((FAILED + 1))
  else
    echo "    ok  (exit 1, names the variable, does not echo the value)"
    sed 's/^/      | /' <<< "$out"
    PASSED=$((PASSED + 1))
  fi
else
  echo "    FAIL: expected exit 1 with an actionable message, got $rc"
  sed 's/^/      | /' <<< "$out"
  FAILED=$((FAILED + 1))
fi

case_header "10b — a MISSING external DSN"
out="$(DATABASE_URL='' ./scripts/compose-render.py --shape prod-external-postgres --out "$MODELS" 2>&1)"; rc=$?
if [ "$rc" = "1" ] && grep -q 'DATABASE_URL is empty' <<< "$out"; then
  echo "    ok  (exit 1, names the variable and the overlay that requires it)"
  sed 's/^/      | /' <<< "$out"
  PASSED=$((PASSED + 1))
else
  echo "    FAIL: expected exit 1, got $rc"; sed 's/^/      | /' <<< "$out"
  FAILED=$((FAILED + 1))
fi

# ---------------------------------------------------------------------------
case_header "11 — a production shape rendered with the component checkouts ABSENT (expects GREEN)"
out="$(./scripts/compose-render.py --shape bundle-no-checkouts --out "$MODELS" 2>&1)"; rc=$?
if [ "$rc" = "0" ]; then
  echo "    ok  (exit 0 - rendered from a tree containing no vizra-core, vizra-user or vizra-search)"
  sed 's/^/      | /' <<< "$out"
  PASSED=$((PASSED + 1))
else
  echo "    FAIL: expected exit 0, got $rc"; sed 's/^/      | /' <<< "$out"
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
  if [ "$rc" = "1" ] && grep -q "SHAPE FLOOR VIOLATION" <<< "$out"; then
    echo "    ok  (exit 1 - the floor refuses a smaller matrix)"
    sed -n '1,6p' <<< "$out" | sed 's/^/      | /'
    PASSED=$((PASSED + 1))
  else
    echo "    FAIL: expected exit 1 with a floor violation, got $rc"
    sed -n '1,6p' <<< "$out" | sed 's/^/      | /'
    FAILED=$((FAILED + 1))
  fi
  revert scripts/compose-shapes.json
  expect "restored" 0
}

# ===========================================================================
# Round 1 of the infrastructure-seat review (2026-09-21). One case per blocking
# finding, plus the two follow-ups that grew a mechanism.
# ===========================================================================

case_header "13 (F1) — compose delivers a key vizra-core has RETIRED"
echo "    (vizra-core 4a80a1e adopted the contract spelling SEARCH_HMAC_KEY and"
echo "     REFUSES VIZRA_SEARCH_HMAC_KEY in production on presence. This mutation"
echo "     reintroduces the old spelling into the compose file, against the REAL"
echo "     retired list in env/registry/core.json - not a planted one.)"
mutate docker-compose.yml <<'PY' && {
import sys
p = sys.argv[1]
s = open(p).read()
old = "  SEARCH_HMAC_KEY: ${SEARCH_HMAC_KEY:?"
assert old in s, "anchor not found"
open(p, "w").write(s.replace(old, "  VIZRA_SEARCH_HMAC_KEY: ${SEARCH_HMAC_KEY:?", 1))
PY
  expect "the retired spelling is back in the compose file" 1 "rule=retired-key-delivered"
  revert docker-compose.yml
  expect "restored" 0
}

case_header "14 (F2) — the MFA-rotation sentence that shipped, back where it shipped"
mutate env/production.env.example <<'PY' && {
import sys
p = sys.argv[1]
s = open(p).read()
old = "# openssl rand -base64 32\n#\n# ***  DO NOT CHANGE"
new = ("# openssl rand -base64 32\n"
       "# ROTATING THIS RE-SEALS STORED MFA SECRETS. `vizra setup --rotate` requires\n"
       "# --yes-i-know for exactly this key.\n"
       "#\n# ***  DO NOT CHANGE")
assert old in s, "anchor not found"
open(p, "w").write(s.replace(old, new, 1))
PY
  expect "the template promises a command that does not exist" 1 "rule=unmarked-future-command"
  revert env/production.env.example
  expect "restored" 0
}

case_header "15 (F3) — a service_healthy gate onto a probe that cannot go red"
mutate docker-compose.yml <<'PY' && {
import sys
p = sys.argv[1]
s = open(p).read()
# Change ONLY the condition. Removing `required: false` as well would make the
# prod-frontend-only shape fail to render, the run would abort before the
# topology checker executed, and the case would "fail" for a reason that has
# nothing to do with the rule it is demonstrating.
old = "        condition: service_started\n"
assert old in s, "anchor not found"
open(p, "w").write(s.replace(old, "        condition: service_healthy\n", 1))
PY
  expect "frontend gates on api's known-false probe" 1 "rule=probe-gates-readiness service=frontend"
  revert docker-compose.yml
  expect "restored" 0
}

case_header "15b (F3) — a known-false declaration that matches nothing any more"
echo "    (the list must not be able to rot into permanent cover)"
mutate scripts/compose-shapes.json <<'PY' && {
import sys, json
p = sys.argv[1]
d = json.load(open(p))
for e in d["known_false_probes"]:
    if e["service"] == "worker":
        e["test"] = ["CMD", "/usr/local/bin/vizra", "healthcheck"]
json.dump(d, open(p, "w"), indent=2); open(p, "a").write("\n")
PY
  expect "a stale known-false declaration" 1 "rule=stale-known-false-probe"
  revert scripts/compose-shapes.json
  expect "restored" 0
}

case_header "16 (F4) — a long-running production service with NO memory cap"
mutate docker-compose.prod.yml <<'PY' && {
import sys
p = sys.argv[1]
s = open(p).read()
old = "    mem_limit: ${VIZRA_WORKER_MEM_LIMIT:-1500m}\n"
assert old in s, "anchor not found"
open(p, "w").write(s.replace(old, "", 1))
PY
  expect "the worker has no containment" 1 "rule=missing-mem-limit service=worker"
  revert docker-compose.prod.yml
  expect "restored" 0
}

case_header "17 (F9) — a compose comment pointing at a file that does not exist"
mutate docker-compose.external-postgres.yml <<'PY' && {
import sys
p = sys.argv[1]
s = open(p).read()
old = "a per-overlay example file that"
assert old in s, "anchor not found"
open(p, "w").write(s.replace(old, "env/external-postgres.env.example, a file that", 1))
PY
  expect "the external-PostgreSQL pointer is dangling" 1 "env/external-postgres.env.example"
  revert docker-compose.external-postgres.yml
  expect "restored" 0
}

# ===========================================================================
# Verifier findings on 69e197e, same fix round.
# ===========================================================================

case_header "18a (V1) — a declared secret must not survive into a WRITTEN model"
echo "    (no file is mutated: the values arrive through the environment, like"
echo "     cases 10a/10b. The renderer used to validate a redacted COPY and then"
echo "     serialise the ORIGINAL, stamped secret_values_redacted: true.)"
rm -rf /tmp/vizra-redaction-demo
# The marker is ASSEMBLED AT RUNTIME rather than written as a literal, and that
# is not decoration. A committed line reading `POSTGRES_PASSWORD='<string>'` is
# a credential-shaped assignment whatever the string says, and a secret scanner
# is right to flag one — GitGuardian flagged exactly this file for it. Building
# the value from parts keeps every committed assignment an interpolation, so the
# demo proves redaction without ever writing something that looks like a secret.
# Do not "simplify" this back to a literal.
MARKER="zz$(printf 'MARK')ERzz"
out="$(env \
  POSTGRES_PASSWORD="${MARKER}PG" \
  VIZRA_SESSION_SECRET="${MARKER}SESSION" \
  VIZRA_MFA_KEY_KEK="${MARKER}KEK" \
  SEARCH_HMAC_KEY="${MARKER}HMAC" \
  CLICKHOUSE_PASSWORD="${MARKER}CLICKHOUSE" \
  DATABASE_URL="postgres://db.ci.invalid:5432/v?sslmode=require&x=${MARKER}DSN" \
  VIZRA_CACHE_URL='rediss://cache.ci.invalid:6379/0' \
  ./scripts/compose-render.py --all --out /tmp/vizra-redaction-demo 2>&1)"; rc=$?
hits="$(grep -ro "$MARKER" /tmp/vizra-redaction-demo 2>/dev/null | wc -l | tr -d ' ')"
if [ "$rc" = "0" ] && [ "$hits" = "0" ]; then
  echo "    ok  (every shape rendered, exit 0; the marker occurs $hits times in the written models)"
  echo "      | the composite DATABASE_URL that docker-compose.yml assembles from"
  echo "      | POSTGRES_PASSWORD is covered too - a by-key replacement alone would not"
  PASSED=$((PASSED + 1))
else
  echo "    FAIL: exit $rc, and the marker occurs $hits time(s) in the written models"
  grep -rl "$MARKER" /tmp/vizra-redaction-demo 2>/dev/null | sed -n '1,5p' | sed 's/^/      | /'
  FAILED=$((FAILED + 1))
fi
rm -rf /tmp/vizra-redaction-demo

case_header "18b (V1) — a key removed from redact_keys must FAIL, not write"
echo "    (redact_keys drives the redaction, secret_keys drives the leak check;"
echo "     because they are independent lists, removing one stops redacting and"
echo "     does NOT stop looking)"
mutate scripts/compose-shapes.json <<'PY' && {
import sys, json
p = sys.argv[1]
d = json.load(open(p))
d["redact_keys"] = [k for k in d["redact_keys"] if k != "POSTGRES_PASSWORD"]
json.dump(d, open(p, "w"), indent=2); open(p, "a").write("\n")
PY
  rm -rf /tmp/vizra-redaction-demo2
  out="$(./scripts/compose-render.py --all --out /tmp/vizra-redaction-demo2 2>&1)"; rc=$?
  written="$(ls /tmp/vizra-redaction-demo2 2>/dev/null | wc -l | tr -d ' ')"
  if [ "$rc" = "1" ] && [ "$written" = "0" ] && grep -q 'survived into the model' <<< "$out"; then
    echo "    ok  (exit 1, $written model(s) written - it refused rather than write a less-redacted file)"
    grep -m2 'survived into the model' <<< "$out" | sed 's/^/      | /'
    PASSED=$((PASSED + 1))
  else
    echo "    FAIL: expected exit 1 with nothing written, got exit $rc and $written file(s)"
    sed -n '1,6p' <<< "$out" | sed 's/^/      | /'
    FAILED=$((FAILED + 1))
  fi
  rm -rf /tmp/vizra-redaction-demo2
  revert scripts/compose-shapes.json
  expect "restored" 0
}

case_header "19 (V3) — a service on a profile NO shape enumerates"
echo "    (the verifier's own pgadmin-tunnel block: it publishes 0.0.0.0:5432 and"
echo "     the lane stayed green, because an unrendered profile is an unasserted one)"
mutate docker-compose.prod.yml <<'PY' && {
import sys
p = sys.argv[1]
block = "\n  pgadmin-tunnel:\n    image: alpine:3.22\n    profiles: [\"backup\"]\n"
block += "    restart: unless-stopped\n    ports:\n      - \"0.0.0.0:5432:5432\"\n"
open(p, "a").write(block)
PY
  expect "an unenumerated profile hides a published datastore port" 1 "rule=profile-not-enumerated"
  revert docker-compose.prod.yml
  expect "restored" 0
}

case_header "20a (V6) — an alias added WITHOUT moving the floor"
mutate env/registry/aliases.json <<'PY' && {
import sys, json
p = sys.argv[1]
d = json.load(open(p))
d["aliases"].append({"operator_key": "VIZRA_SITE_HANDLE",
    "service_keys": [{"component": "vizra-core", "key": "VIZRA_SITE_HANDLE"}],
    "authorised": True, "authorised_by": "nobody", "removed_when": "never"})
json.dump(d, open(p, "w"), indent=2); open(p, "a").write("\n")
PY
  expect "the alias floor was not moved in the same edit" 1 "rule=alias-floor"
  revert env/registry/aliases.json
  expect "restored" 0
}

case_header "20b (V6) — an alias whose service key is NOT in the snapshot"
mutate env/registry/aliases.json <<'PY' && {
import sys, json
p = sys.argv[1]
d = json.load(open(p))
d["aliases"][0]["service_keys"][0]["key"] = "VIZRA_SEARCH_HMAC_KEY_RENAMED_UPSTREAM"
json.dump(d, open(p, "w"), indent=2); open(p, "a").write("\n")
PY
  expect "the alias target no longer exists upstream" 1 "rule=alias-unwired"
  revert env/registry/aliases.json
  expect "restored" 0
}

case_header "21 (V8) — a port allowed on TCP, published on UDP"
mutate docker-compose.prod.yml <<'PY' && {
import sys
p = sys.argv[1]
s = open(p).read()
old = '- !override "127.0.0.1:${VIZRA_HTTP_PORT:-8080}:8080"'
assert old in s, "anchor not found"
open(p, "w").write(s.replace(old, old[:-1] + '/udp"', 1))
PY
  expect "the allowlist is protocol-aware" 1 "rule=port-not-allowed service=api"
  revert docker-compose.prod.yml
  expect "restored" 0
}
# ===========================================================================
# Round 2: the three statements that were untrue as written, and the
# /dev/shm default nobody had noticed.
# ===========================================================================

case_header "22 (F2) — a shell script described in the PRESENT tense"
echo "    (the exact line that survived round 1: backup.sh does not exist, and an"
echo "     operator who believes it does defers setting up provider snapshots)"
mutate env/production.env.example <<'PY' && {
import sys
p = sys.argv[1]
s = open(p).read()
old = "# latency and never data. Nothing backs the cache up today; backup.sh\n# (VZ-ISSUE-004) will refuse to, and say why."
new = "# latency and never data. `backup.sh` refuses to back the cache up, and says so."
assert old in s, "anchor not found"
open(p, "w").write(s.replace(old, new, 1))
PY
  expect "a present-tense claim about a script that does not exist" 1 "rule=unmarked-future-script"
  revert env/production.env.example
  expect "restored" 0
}

case_header "23 (F3) — a known-false probe with no operator-facing disclosure"
echo "    (the machine half is printed on every run; this is the half for the"
echo "     person running docker compose ps at 3am)"
mutate README.md <<'PY' && {
import sys
p = sys.argv[1]
s = open(p).read()
old = "IGNORE THE `healthy` COLUMN"
assert old in s, "anchor not found"
open(p, "w").write(s.replace(old, "IGNORE THE health column", 1))
PY
  expect "the disclosure went missing while the list stands" 1 "rule=known-false-undisclosed"
  revert README.md
  expect "restored" 0
}

case_header "24 (NEW-1) — postgres left on Docker's 64 MiB /dev/shm"
echo "    (starts a cluster fine; fails parallel plans months later with"
echo "     'No space left on device' on a host with gigabytes free)"
mutate docker-compose.yml <<'PY' && {
import sys
p = sys.argv[1]
s = open(p).read()
old = "    shm_size: ${VIZRA_POSTGRES_SHM_SIZE:-256m}\n"
assert old in s, "anchor not found"
open(p, "w").write(s.replace(old, "", 1))
PY
  expect "postgres on the 64 MiB default" 1 "rule=postgres-shm-floor service=postgres"
  revert docker-compose.yml
  expect "restored" 0
}
# ===========================================================================
# Verifier re-verification findings at 3261ad3.
# ===========================================================================

case_header "25 (R-1) — a NEW secret key, added the fully correct way"
echo "    (the verifier's own mutation: declared \"secret\": true in the registry,"
echo "     documented in the template, delivered by compose. Before the fix it was"
echo "     written raw into all 13 models - 47 occurrences - under a"
echo "     secret_values_redacted: true stamp, with all four checkers green.)"
mutate env/registry/core.json <<'PY' && {
import sys, json
p = sys.argv[1]
d = json.load(open(p))
d["keys"].append({"name": "VIZRA_SMTP_PASSWORD", "required": "optional",
                  "secret": True, "delivered_by": "template"})
json.dump(d, open(p, "w"), indent=2); open(p, "a").write("\n")
PY
  expect "a secret-flagged key that nobody classified" 1 "rule=unclassified-secret-key"
  revert env/registry/core.json
  expect "restored" 0
}

case_header "25b (R-1) — and its value must never reach a written model"
echo "    (the same key, delivered end to end, rendered with a recognisable value)"
cp env/registry/core.json /tmp/vizra-r1-reg.bak
cp docker-compose.yml /tmp/vizra-r1-dc.bak
python3 - <<'PY'
import json
s = open("docker-compose.yml").read()
a = "  VIZRA_SHUTDOWN_GRACE: ${VIZRA_SHUTDOWN_GRACE:-20s}"
open("docker-compose.yml", "w").write(
    s.replace(a, a + "\n  VIZRA_SMTP_PASSWORD: ${VIZRA_SMTP_PASSWORD:-}", 1))
d = json.load(open("env/registry/core.json"))
d["keys"].append({"name": "VIZRA_SMTP_PASSWORD", "required": "optional",
                  "secret": True, "delivered_by": "template"})
json.dump(d, open("env/registry/core.json", "w"), indent=2)
open("env/registry/core.json", "a").write("\n")
PY
SMTPMARK="zz$(printf REALSMTP)SECRETzz"
rm -rf /tmp/vizra-r1-models
env VIZRA_SMTP_PASSWORD="$SMTPMARK" ./scripts/compose-render.py --all --out /tmp/vizra-r1-models >/dev/null 2>&1; rc=$?
n="$(grep -rc "$SMTPMARK" /tmp/vizra-r1-models 2>/dev/null | awk -F: '{s+=$2} END{print s+0}')"
if [ "$rc" = "0" ] && [ "$n" = "0" ]; then
  echo "    ok  (rendered exit 0; the value occurs $n times across the written models)"
  echo "      | the redaction set is DERIVED from the registry's own secret flag,"
  echo "      | so a key nobody added to redact_keys is still protected on the bytes"
  PASSED=$((PASSED + 1))
else
  echo "    FAIL: exit $rc, value present $n time(s)"
  FAILED=$((FAILED + 1))
fi
rm -rf /tmp/vizra-r1-models
cp /tmp/vizra-r1-reg.bak env/registry/core.json; cp /tmp/vizra-r1-dc.bak docker-compose.yml
rm -f /tmp/vizra-r1-reg.bak /tmp/vizra-r1-dc.bak
expect "restored" 0

case_header "26 (R-3) — a REAL probe swapped for one that cannot fail"
echo "    (probe-gates-readiness only refuses a gate onto a probe someone"
echo "     DECLARED false; this is the converse it cannot see)"
mutate docker-compose.yml <<'PY' && {
import sys, re
p = sys.argv[1]
s = open(p).read()
m = re.search(r'      test: \["CMD-SHELL", "pg_isready[^\n]*\n', s)
assert m, "anchor not found"
open(p, "w").write(s[:m.start()] + '      test: ["CMD", "true"]\n' + s[m.end():])
PY
  expect "postgres gates three edges on a probe that cannot fail" 1 "rule=gated-probe-unrecognised service=postgres"
  revert docker-compose.yml
  expect "restored" 0
}

# ===========================================================================
# CLOSING ROUND. Verifier findings S-1…S-7 and infrastructure NEW-2/NEW-3 at
# 9c4b5d3. Every one of them is the same defect: a checker that matches TEXT,
# described in this repository's own documents with a guarantee word. These
# cases are what make the sentences true rather than softer.
# ===========================================================================

# ---------------------------------------------------------------------------
# S-2. The four probes the verifier measured GREEN on 9c4b5d3 while always
# exiting ZERO — so all three service_healthy gates onto PostgreSQL gated on
# nothing — plus the disabled spelling. The old rule was
# `must_invoke not in joined`, a substring test over the joined command line,
# while docs/META_REPO.md and docs/quality/COMMANDS.md both said "invoke".
# Each is applied to postgres, which api, worker and migrate gate on.
#
# What these cases do NOT establish, stated here so the transcript cannot be
# read as more than it is: `["CMD-SHELL", "pg_isready --version"]` passes the
# rule and always succeeds. Proving a probe can go RED needs a running
# container, which is VZ-ISSUE-004's boot lane.
probe_case() {
  local id="$1" why="$2" probe="$3"
  case_header "$id (S-2) — $why"
  echo "    (rendered probe: $probe)"
  export PROBE_JSON="$probe"
  mutate docker-compose.yml <<'PY' && {
import sys, os, re
p = sys.argv[1]
s = open(p).read()
m = re.search(r'      test: \["CMD-SHELL", "pg_isready[^\n]*\n', s)
assert m, "anchor not found"
open(p, "w").write(s[:m.start()] + "      test: " + os.environ["PROBE_JSON"] + "\n" + s[m.end():])
PY
    expect "$why" 1 "rule=gated-probe-unrecognised service=postgres"
    revert docker-compose.yml
    expect "restored" 0
  }
}

probe_case "26a" "a probe that always succeeds behind || true" \
  '["CMD-SHELL", "pg_isready -U vizra || true"]'
probe_case "26b" "the declared command demoted to a shell COMMENT" \
  '["CMD-SHELL", "true # pg_isready"]'
probe_case "26c" "a second statement after an unconditional exit 0" \
  '["CMD", "sh", "-c", "exit 0; pg_isready"]'
probe_case "26d" "the declared command ECHOED rather than run" \
  '["CMD", "echo", "pg_isready"]'
probe_case "26e" "the healthcheck DISABLED under a service_healthy gate" \
  '["NONE"]'


case_header "27 (S-1 / NEW-2) — known_false_probes EMPTIED while the paragraphs stand"
echo "    (the direction three documents and the PR body claimed was enforced and"
echo "     was not: the rule body sat inside \`if known_false and disclosure:\`, so"
echo "     an empty list made it unreachable and the lane exited 0)"
mutate scripts/compose-shapes.json <<'PY' && {
import sys, json
p = sys.argv[1]
d = json.load(open(p))
assert d["known_false_probes"], "the list is already empty; this case proves nothing"
d["known_false_probes"] = []
json.dump(d, open(p, "w"), indent=2); open(p, "a").write("\n")
PY
  expect "the disclosure outlived the probes it describes" 1 "rule=known-false-stale-disclosure"
  revert scripts/compose-shapes.json
  expect "restored" 0
}

# ---------------------------------------------------------------------------
# S-3. The script pass missed exactly the two spellings an operator-facing
# document uses for a runnable script, and `unknown-script` could not fire at
# all. Each of these replaces the same correctly-marked sentence in the
# production template with a present-tense claim, as case 22 does for the bare
# form.
script_case() {
  local id="$1" why="$2" text="$3" want="$4"
  case_header "$id (S-3) — $why"
  export SCRIPT_TEXT="$text"
  mutate env/production.env.example <<'PY' && {
import sys, os
p = sys.argv[1]
s = open(p).read()
old = ("# latency and never data. Nothing backs the cache up today; backup.sh\n"
       "# (VZ-ISSUE-004) will refuse to, and say why.")
assert old in s, "anchor not found"
open(p, "w").write(s.replace(old, "# latency and never data. " + os.environ["SCRIPT_TEXT"], 1))
PY
    expect "$why" 1 "$want"
    revert env/production.env.example
    expect "restored" 0
  }
}

script_case "28a" "a PATH-form script reference, unmarked" \
  './backup.sh refuses to back the cache up, and says so.' \
  "rule=unmarked-future-script"
script_case "28b" "a scripts/ -prefixed reference, unmarked" \
  'scripts/backup.sh refuses to back the cache up, and says so.' \
  "rule=unmarked-future-script"
script_case "28c" "a BACKTICKED path form, unmarked" \
  '`./backup.sh` refuses to back the cache up, and says so.' \
  "rule=unmarked-future-script"
script_case "28d" "an INVENTED script nobody declared" \
  'rotate-secrets.sh rotates the cache credentials nightly.' \
  "rule=unknown-script"

case_header "28e (S-3) — a path form WITH its marker in the window stays GREEN"
echo "    (the generalised matcher must not make correct documentation illegal:"
echo "     the marker is one line below, inside MARKER_WINDOW)"
mutate env/production.env.example <<'PY' && {
import sys
p = sys.argv[1]
s = open(p).read()
old = "(backup.sh, which will"
assert old in s, "anchor not found"
open(p, "w").write(s.replace(old, "(./backup.sh, which will", 1))
PY
  expect "./backup.sh with VZ-ISSUE-004 one line below" 0
  revert env/production.env.example
  expect "restored" 0
}
# ---------------------------------------------------------------------------
echo
echo "=============================================================="
echo "RESULT: $PASSED assertion(s) passed, $FAILED failed, across $CASES case(s)"
echo "final tree digest check:"
dirty="$(git status --porcelain)"
sed 's/^/  /' <<< "$dirty"
if [ -n "$dirty" ]; then
  echo "  !! THE TREE IS NOT CLEAN. Either a restore above did not land, or a"
  echo "     step before this one left a file behind. Both matter: this check is"
  echo "     what proves the mutations were reverted, and it cannot tell the two"
  echo "     apart, so anything untracked has to be accounted for."
  exit 1
fi
echo "  tree is clean - every mutation was reverted"
[ "$FAILED" = "0" ] || exit 1
