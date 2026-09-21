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
              && ./scripts/check-config-coverage.py "$MODELS" \
              && ./scripts/check-template-claims.py \
              && ./scripts/check-doc-links.py; } 2>&1 )"
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

# ===========================================================================
# Round 1 of the infrastructure-seat review (2026-09-21). One case per blocking
# finding, plus the two follow-ups that grew a mechanism.
# ===========================================================================

case_header "13 (F1) — compose delivers a key vizra-core has RETIRED"
echo "    (core refuses a retired name in production ON PRESENCE, so delivering"
echo "     both spellings is a guaranteed boot refusal, not belt-and-braces)"
mutate env/registry/core.json <<'PY' && {
import sys, json
p = sys.argv[1]
d = json.load(open(p))
d["retired_keys"] = ["VIZRA_SEARCH_HMAC_KEY"]
json.dump(d, open(p, "w"), indent=2); open(p, "a").write("\n")
PY
  expect "a retired key is still delivered" 1 "rule=retired-key-delivered"
  revert env/registry/core.json
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
out="$(env \
  POSTGRES_PASSWORD='zzMARKERzzPOSTGRESzz' \
  VIZRA_SESSION_SECRET='zzMARKERzzSESSIONzz' \
  VIZRA_MFA_KEY_KEK='zzMARKERzzKEKzz' \
  SEARCH_HMAC_KEY='zzMARKERzzHMACzz' \
  CLICKHOUSE_PASSWORD='zzMARKERzzCLICKHOUSEzz' \
  DATABASE_URL='postgres://db.ci.invalid:5432/v?sslmode=require&x=zzMARKERzzDSNzz' \
  VIZRA_CACHE_URL='rediss://cache.ci.invalid:6379/0' \
  ./scripts/compose-render.py --all --out /tmp/vizra-redaction-demo 2>&1)"; rc=$?
hits="$(grep -ro 'zzMARKERzz' /tmp/vizra-redaction-demo 2>/dev/null | wc -l | tr -d ' ')"
if [ "$rc" = "0" ] && [ "$hits" = "0" ]; then
  echo "    ok  (every shape rendered, exit 0; the marker occurs $hits times in the written models)"
  echo "      | the composite DATABASE_URL that docker-compose.yml assembles from"
  echo "      | POSTGRES_PASSWORD is covered too - a by-key replacement alone would not"
  PASSED=$((PASSED + 1))
else
  echo "    FAIL: exit $rc, and the marker occurs $hits time(s) in the written models"
  grep -rl 'zzMARKERzz' /tmp/vizra-redaction-demo 2>/dev/null | sed 's/^/      | /' | head -5
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
  if [ "$rc" = "1" ] && [ "$written" = "0" ] && printf '%s\n' "$out" | grep -q 'survived into the model'; then
    echo "    ok  (exit 1, $written model(s) written - it refused rather than write a less-redacted file)"
    printf '%s\n' "$out" | grep -m2 'survived into the model' | sed 's/^/      | /'
    PASSED=$((PASSED + 1))
  else
    echo "    FAIL: expected exit 1 with nothing written, got exit $rc and $written file(s)"
    printf '%s\n' "$out" | sed 's/^/      | /' | head -6
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
# ---------------------------------------------------------------------------
echo
echo "=============================================================="
echo "RESULT: $PASSED assertion(s) passed, $FAILED failed"
echo "final tree digest check:"
dirty="$(git status --porcelain)"
printf '%s\n' "$dirty" | sed 's/^/  /'
if [ -n "$dirty" ]; then
  echo "  !! THE TREE IS NOT CLEAN. Either a restore above did not land, or a"
  echo "     step before this one left a file behind. Both matter: this check is"
  echo "     what proves the mutations were reverted, and it cannot tell the two"
  echo "     apart, so anything untracked has to be accounted for."
  exit 1
fi
echo "  tree is clean - every mutation was reverted"
[ "$FAILED" = "0" ] || exit 1
