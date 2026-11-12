#!/usr/bin/env bash
# boot-lane.sh — the meta `boot` lane (VZ-CI-003, VZ-ISSUE-004; transcripts
# for VZ-FOUND-005). Boots the PRODUCTION compose shape from source with dummy
# secrets and asserts, in order:
#   1. the migrate one-shot, run from the service image, exits 0 within
#      BOOT_MIGRATE_TIMEOUT (run twice: apply, then idempotent re-run);
#   2. negative self-test: with tests/boot/migrate-never-exits.yml the same
#      bounded run is killed by the timeout (a one-shot that keeps running
#      fails the lane rather than hanging it);
#   3. `up -d --no-build --wait`: every started service healthy, api /readyz 200;
#   4. fault injection: stop postgres -> /readyz non-200 within
#      BOOT_READY_INTERVAL; start postgres -> /readyz 200 again with the api
#      container NOT restarted (same StartedAt, same RestartCount).
# NOT covered (left open on VZ-CI-003): fixture JPEG upload + decoded thumbnail
# hash — needs the M1 upload API, which does not exist yet.
#
# Env: VIZRA_DIR (component checkouts, default repo root), BOOT_OUT (artifact
# dir), BOOT_MIGRATE_TIMEOUT (s, 180), BOOT_READY_INTERVAL (s, 30),
# BOOT_EXTRA_COMPOSE (extra -f overlay applied to every step; demo only),
# BOOT_SKIP_BUILD=1 (reuse images already tagged).
# The generated env file holds dummy secrets only, is mode 600 and is never printed.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VIZRA_DIR="${VIZRA_DIR:-$ROOT}"
OUT="${BOOT_OUT:-$ROOT/boot-out}"
MIGRATE_TIMEOUT="${BOOT_MIGRATE_TIMEOUT:-180}"
READY_INTERVAL="${BOOT_READY_INTERVAL:-30}"
TAG="boot-local"
PROJECT="vizra-boot"
API="http://127.0.0.1:8080"
mkdir -p "$OUT"
ENV_FILE="$(mktemp)"
chmod 600 "$ENV_FILE"

log() { printf 'boot: %s\n' "$*"; }
die() { printf 'boot: FAIL %s\n' "$*" >&2; exit 1; }

compose() {
  local extra=()
  if [ -n "${BOOT_EXTRA_COMPOSE:-}" ]; then extra=(-f "$BOOT_EXTRA_COMPOSE"); fi
  docker compose -p "$PROJECT" --project-directory "$ROOT" \
    -f "$ROOT/docker-compose.yml" -f "$ROOT/docker-compose.prod.yml" "${extra[@]}" \
    --env-file "$ENV_FILE" --profile core --profile frontend "$@"
}

cleanup() {
  local rc=$?
  compose logs --no-color --timestamps >"$OUT/compose-logs.txt" 2>&1 || true
  compose ps -a >"$OUT/compose-ps.txt" 2>&1 || true
  # Dummy secrets must not appear in the artifact even though they are dummy:
  # the check is what would catch a real one leaking on a real host.
  while IFS='=' read -r k v; do
    case "$k" in *SECRET*|*KEK*|*HMAC*|*PASSWORD*) ;; *) continue ;; esac
    if [ -n "$v" ] && grep -qF -- "$v" "$OUT"/compose-*.txt; then
      echo "boot: FAIL secret value of $k appears in compose logs; artifact withheld" >&2
      rm -f "$OUT"/compose-*.txt; rc=1
    fi
  done <"$ENV_FILE"
  compose down -v --remove-orphans >/dev/null 2>&1 || true
  rm -f "$ENV_FILE"
  log "exit $rc"
  exit "$rc"
}
trap cleanup EXIT

# --- sources and images ------------------------------------------------------
for c in vizra-core vizra-user; do
  [ -d "$VIZRA_DIR/$c/.git" ] || [ -f "$VIZRA_DIR/$c/.git" ] || die "$c not checked out (run bootstrap.sh)"
  printf '%s %s\n' "$c" "$(git -C "$VIZRA_DIR/$c" rev-parse HEAD)" | tee -a "$OUT/component-shas.txt"
done
if [ "${BOOT_SKIP_BUILD:-0}" != 1 ]; then
  docker build -q -t "ghcr.io/yegamble/vizra-core:$TAG" \
    --build-arg COMMIT="$(git -C "$VIZRA_DIR/vizra-core" rev-parse HEAD)" "$VIZRA_DIR/vizra-core"
  docker build -q -t "ghcr.io/yegamble/vizra-user:$TAG" "$VIZRA_DIR/vizra-user"
fi

# --- dummy-secret env file (never printed) ----------------------------------
# `vizra setup` does not exist yet (vizra has version/doctor/migrate/healthcheck),
# so the generator is openssl. Every value is random and thrown away.
{
  echo "VIZRA_CORE_TAG=$TAG"
  echo "VIZRA_USER_TAG=$TAG"
  echo "VIZRA_SEARCH_TAG=$TAG"
  echo "VIZRA_PUBLIC_ORIGIN=https://boot.vizra.invalid"
  echo "VIZRA_DOMAIN=boot.vizra.invalid"
  echo "POSTGRES_PASSWORD=$(openssl rand -hex 24)"
  echo "VIZRA_SESSION_SECRET=$(openssl rand -base64 32)"
  echo "VIZRA_MFA_KEY_KEK=$(openssl rand -base64 32)"
  echo "SEARCH_HMAC_KEY=$(openssl rand -hex 32)"
} >"$ENV_FILE"

compose config --quiet || die "production shape does not render"
# Third-party images (digest-pinned) are pulled; Vizra images are the local builds,
# so every later step runs with --pull never.
compose pull --quiet postgres redis

# --- 1/2. migrate one-shot bounded ------------------------------------------
run_migrate() { # $1 label; returns the bounded run's exit status
  local rc=0
  timeout --kill-after=10 "$MIGRATE_TIMEOUT" \
    docker compose -p "$PROJECT" --project-directory "$ROOT" -f "$ROOT/docker-compose.yml" \
    -f "$ROOT/docker-compose.prod.yml" ${2:+-f "$2"} --env-file "$ENV_FILE" \
    --profile core --profile frontend run --rm --pull never migrate || rc=$?
  log "migrate[$1] exit=$rc (timeout ${MIGRATE_TIMEOUT}s)"
  return "$rc"
}
for pass in apply rerun; do
  run_migrate "$pass" "${BOOT_EXTRA_COMPOSE:-}" || die "migrate one-shot ($pass) did not exit 0 within ${MIGRATE_TIMEOUT}s"
done

if [ -z "${BOOT_EXTRA_COMPOSE:-}" ]; then
  rc=0
  MIGRATE_TIMEOUT=20 run_migrate never-exits "$ROOT/tests/boot/migrate-never-exits.yml" || rc=$?
  [ "$rc" = 124 ] || [ "$rc" = 137 ] || die "negative self-test: never-exiting migrate gave exit $rc, expected timeout (124/137)"
  compose rm -fsv migrate >/dev/null 2>&1 || true
  docker ps -q --filter "label=com.docker.compose.project=$PROJECT" --filter "label=com.docker.compose.service=migrate" | xargs -r docker rm -f >/dev/null
  log "negative self-test PASS: a migrate that never exits is killed by the timeout"
fi

# --- 3. boot ---------------------------------------------------------------
timeout 600 docker compose -p "$PROJECT" --project-directory "$ROOT" -f "$ROOT/docker-compose.yml" \
  -f "$ROOT/docker-compose.prod.yml" --env-file "$ENV_FILE" --profile core --profile frontend \
  up -d --no-build --pull never --wait --wait-timeout 300 || die "stack did not become healthy"
compose ps -a

code() { curl -s -o /dev/null -m 5 -w '%{http_code}' "$API/readyz" || true; }
c="$(code)"; [ "$c" = 200 ] || die "/readyz=$c after boot, want 200"
log "/readyz 200 after boot"

# --- 4. fault injection ----------------------------------------------------
api_id="$(compose ps -q api)"
before="$(docker inspect -f '{{.State.StartedAt}} {{.RestartCount}}' "$api_id")"
compose stop postgres
t0=$SECONDS; c=200
while [ $((SECONDS - t0)) -le "$READY_INTERVAL" ]; do
  c="$(code)"; [ "$c" != 200 ] && break; sleep 1
done
[ "$c" != 200 ] || die "/readyz still 200 ${READY_INTERVAL}s after postgres stopped"
log "/readyz=$c $((SECONDS - t0))s after postgres stopped (bound ${READY_INTERVAL}s)"
compose start postgres
t0=$SECONDS
while [ $((SECONDS - t0)) -le 120 ]; do
  c="$(code)"; [ "$c" = 200 ] && break; sleep 2
done
[ "$c" = 200 ] || die "/readyz=$c 120s after postgres restarted"
after="$(docker inspect -f '{{.State.StartedAt}} {{.RestartCount}}' "$api_id")"
[ "$before" = "$after" ] || die "api restarted during recovery ($before -> $after)"
log "/readyz 200 again $((SECONDS - t0))s after postgres start; api not restarted ($after)"
log "PASS"
