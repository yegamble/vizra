#!/usr/bin/env bash
# VZ-CI-002 / VZ-OPS-008 negative cases, run on a THROWAWAY COPY of the tree so
# the checkout is never mutated. Each case: baseline green, mutation red with the
# named rule, digest proof the mutation applied.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
PASSED=0; FAILED=0

fresh() {
  rm -rf "$WORK/t"; mkdir -p "$WORK/t"
  (cd "$ROOT" && git ls-files -co --exclude-standard -z | tar --null -T - -cf -) | tar -xf - -C "$WORK/t"
}

# expect <label> <shape> <want_rc> [rule-signal]
expect() {
  local label="$1" shape="$2" want="$3" sig="${4:-}" out rc
  out="$(cd "$WORK/t" && rm -rf m && ./scripts/compose-render.py --all --out m 2>&1 \
         && ./scripts/check-compose-topology.py m 2>&1)"; rc=$?
  if [ "$rc" != "$want" ] || { [ -n "$sig" ] && ! grep -qF "$sig" <<<"$out"; }; then
    echo "FAIL  $label: rc=$rc want=$want signal='${sig}'"; grep -E 'VIOLATION|FAIL' <<<"$out" | head -5
    FAILED=$((FAILED+1)); return
  fi
  echo "ok    $label [$shape]: rc=$rc${sig:+ ($sig)}"; PASSED=$((PASSED+1))
}

# mutate <file> <python: s -> s>
mutate() {
  local f="$WORK/t/$1" before after
  before="$(shasum -a 256 "$f" | cut -c1-16)"
  python3 - "$f" "$2" <<'PY'
import sys
p, expr = sys.argv[1], sys.argv[2]
s = open(p).read(); n = eval(expr, {"s": s}); assert n != s; open(p, "w").write(n)
PY
  after="$(shasum -a 256 "$f" | cut -c1-16)"
  [ "$before" != "$after" ] || { echo "FAIL  mutation did not apply to $1"; FAILED=$((FAILED+1)); return 1; }
  echo "      mutated $1 $before -> $after"
}

fresh
expect "baseline prod-all-optional" prod-all-optional 0
expect "baseline bundle-no-checkouts" bundle-no-checkouts 0

# VZ-OPS-008 negative: a service mounting docker.sock fails CI.
fresh
mutate docker-compose.prod.yml 's.replace("    pull_policy: always\n    build: !reset null\n    environment:\n      VIZRA_MODE: production\n    ports:", "    pull_policy: always\n    build: !reset null\n    volumes:\n      - /var/run/docker.sock:/var/run/docker.sock\n    environment:\n      VIZRA_MODE: production\n    ports:", 1)' \
  && expect "api mounts docker.sock" prod-default 1 "rule=docker-socket service=api"

# VZ-OPS-008: no-new-privileges removed from the shared hardening fragment.
fresh
mutate docker-compose.yml 's.replace("x-hardening: &hardening\n  security_opt:\n    - \"no-new-privileges:true\"", "x-hardening: &hardening\n  security_opt: []", 1)' \
  && expect "hardening drops no-new-privileges" prod-default 1 "rule=no-new-privileges"

# VZ-OPS-008: logs uncapped (max-file removed from the shared logging fragment).
fresh
mutate docker-compose.yml 's.replace("    max-file: \"5\"\n", "", 1)' \
  && expect "log cap loses max-file" prod-default 1 "rule=missing-log-cap"

# VZ-CI-002 negative: a NEW optional service publishing 0.0.0.0 fails port
# closure (an existing datastore would trip never-published instead; see below).
fresh
mutate docker-compose.yml 's.replace("  clickhouse:\n", "  newopt:\n    image: busybox:1.37@sha256:" + "a"*64 + "\n    profiles: [\"analytics\"]\n    ports:\n      - \"0.0.0.0:9999:9999\"\n\n  clickhouse:\n", 1)' \
  && expect "new optional service publishes 0.0.0.0" prod-all-optional 1 "rule=port-not-allowed service=newopt"
fresh
mutate docker-compose.prod.yml 's.replace("  clickhouse:\n    restart: unless-stopped\n", "  clickhouse:\n    restart: unless-stopped\n    ports:\n      - \"0.0.0.0:8123:8123\"\n", 1)' \
  && expect "optional clickhouse publishes 0.0.0.0" prod-all-optional 1 "rule=never-published service=clickhouse"

# VZ-OPS-008 "secrets untracked".
fresh
if (cd "$WORK/t" && git init -q && git add -A >/dev/null && ./scripts/check-secrets-untracked.sh . >/dev/null); then
  echo "ok    secrets-untracked baseline"; PASSED=$((PASSED+1))
else echo "FAIL  secrets-untracked baseline"; FAILED=$((FAILED+1)); fi
if (cd "$WORK/t" && echo 'POSTGRES_PASSWORD=x' > env/production.env && git add -f env/production.env \
    && out="$(./scripts/check-secrets-untracked.sh . 2>&1)"; [ $? = 1 ] && grep -q 'rule=tracked-secret-file' <<<"$out"); then
  echo "ok    tracked env/production.env: rc=1 (rule=tracked-secret-file)"; PASSED=$((PASSED+1))
else echo "FAIL  tracked env/production.env not caught"; FAILED=$((FAILED+1)); fi

echo "passed=$PASSED failed=$FAILED"
[ "$FAILED" = 0 ] && [ "$PASSED" = 9 ]
