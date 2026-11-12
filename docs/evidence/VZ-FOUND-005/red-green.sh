#!/usr/bin/env bash
# VZ-FOUND-005 meta: red/green for the required-probe rule on api and worker.
# Mutates docker-compose.yml, restores it on any exit. Run from the meta root.
set -u -o pipefail
M="$(mktemp -d)"
cp docker-compose.yml "$M/orig.yml"
trap 'cp "$M/orig.yml" docker-compose.yml; rm -rf "$M"' EXIT
check() {
  ./scripts/compose-render.py --all --out "$M/models" >/dev/null \
    && ./scripts/check-compose-topology.py "$M/models"
  echo "exit=$?"
}
echo "# VZ-FOUND-005 meta red/green, tree $(git rev-parse HEAD)"
for svc in api worker; do
  python3 - "$svc" <<'PY'
import sys
svc = sys.argv[1]
s = open("docker-compose.yml").read()
old = f'"/usr/local/bin/vizra", "healthcheck", "{svc}"]'
assert s.count(old) == 1, "anchor not found"
open("docker-compose.yml", "w").write(s.replace(old, '"/usr/local/bin/vizra", "version"]'))
PY
  echo "## MUTATION: $svc probe -> vizra version"
  check
  cp "$M/orig.yml" docker-compose.yml
  echo "## RESTORED ($svc)"
  check
done
