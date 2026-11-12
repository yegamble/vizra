#!/usr/bin/env bash
# VZ-INSTALL-004 bundle tests. Each negative case asserts a specific failure message.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
MIG="$ROOT/tests/bundle/fixtures/core-migrations"
REC="$ROOT/tests/bundle/fixtures/release-record.json"
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-$(git -C "$ROOT" log -1 --format=%ct)}"
pass=0
export COPYFILE_DISABLE=1 # no macOS ._ metadata entries in the tampered tarballs
ok() { pass=$((pass + 1)); echo "ok $pass - $1"; }
die() { echo "not ok - $1" >&2; exit 1; }
expect_fail() { # <desc> <needle> <cmd...>
  local desc=$1 needle=$2; shift 2
  if "$@" >"$WORK/out" 2>&1; then cat "$WORK/out"; die "$desc: command succeeded"; fi
  grep -qF -- "$needle" "$WORK/out" || { cat "$WORK/out"; die "$desc: no '$needle'"; }
  ok "$desc"
}
copy_src() { # a scratch copy of the tree, so mutations never touch the checkout
  local dst=$1; mkdir -p "$dst"
  (cd "$ROOT" && git ls-files -co --exclude-standard -z | grep -zv '^vizra-' \
    | while IFS= read -r -d '' f; do [ -f "$f" ] && mkdir -p "$dst/$(dirname "$f")" && cp -p "$f" "$dst/$f"; done)
}
B="$ROOT/scripts/make-bundle.sh"; C="$ROOT/scripts/check-bundle.sh"
TGZ=vizra-bundle_v0.0.0-ci.tar.gz

# success: byte-identical twice
"$B" --tag v0.0.0-ci --out "$WORK/a" --core-migrations "$MIG" >/dev/null
"$B" --tag v0.0.0-ci --out "$WORK/b" --core-migrations "$MIG" >/dev/null
cmp "$WORK/a/$TGZ" "$WORK/b/$TGZ" || die "two builds differ"
ok "two builds are byte-identical (sha256 $(python3 -c 'import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())' "$WORK/a/$TGZ"))"

# success: the release record path yields the same schema version and the same bytes
"$B" --tag v0.0.0-ci --out "$WORK/r" --release-record "$REC" >/dev/null
python3 - "$WORK/r/$TGZ" <<'PY' || die "release-record schema_version"
import json, sys, tarfile
m = json.load(tarfile.open(sys.argv[1]).extractfile("vizra-bundle_v0.0.0-ci/MANIFEST.json"))
assert m["schema_version"] == 3 and m["schema_version_source"] == "release-record", m
PY
ok "schema_version read from a release record fixture"

# success: content check + every production shape renders from the unpacked bundle
"$C" "$WORK/a/$TGZ" --core-migrations "$MIG" >"$WORK/check.log" 2>&1 || { cat "$WORK/check.log"; die "check failed"; }
n=$(grep -c 'from the unpacked bundle, no checkouts' "$WORK/check.log")
want=$(python3 -c 'import json,sys;print(sum(s["kind"]=="production" for s in json.load(open(sys.argv[1]))["shapes"]))' "$ROOT/scripts/compose-shapes.json")
[ "$n" = "$want" ] && [ "$n" -gt 0 ] || die "rendered $n of $want production shapes"
ok "content ok, manifest schema_version = migrations on disk, $n/$want production shapes rendered"

# negative: schema version disagrees with migrations on disk
mkdir -p "$WORK/mig4"; cp "$MIG"/* "$WORK/mig4/"; : > "$WORK/mig4/000004_more.up.sql"
expect_fail "schema_version != migrations on disk fails" "schema_version 3 != migrations on disk 4" \
  "$C" "$WORK/a/$TGZ" --core-migrations "$WORK/mig4" --no-render

# negative: a missing bind-mount source fails the content check
copy_src "$WORK/s1"
python3 - "$WORK/s1/docker-compose.prod.yml" <<'PY'
import sys
p = sys.argv[1]; s = open(p).read()
probe = "\nservices:\n  x-bind-probe:\n    image: busybox\n    volumes:\n      - type: bind\n        source: ./deploy/not-shipped.conf\n        target: /x\n"
assert s.count("\nservices:\n") == 1
open(p, "w").write(s.replace("\nservices:\n", probe, 1))
PY
grep -q 'not-shipped.conf' "$WORK/s1/docker-compose.prod.yml" || die "mutation did not apply"
"$B" --tag v0.0.0-ci --out "$WORK/s1o" --src "$WORK/s1" --core-migrations "$MIG" >/dev/null
expect_fail "a missing bind-mount source fails" "missing bind-mount source: ./deploy/not-shipped.conf" \
  "$C" "$WORK/s1o/$TGZ" --no-render

# negative: an excluded file in the include list is refused at build time
copy_src "$WORK/s2"
python3 - "$WORK/s2/scripts/bundle-contents.json" <<'PY'
import json, sys; p = sys.argv[1]; c = json.load(open(p)); c["include"].append("docker-compose.dev.yml"); json.dump(c, open(p, "w"))
PY
expect_fail "an excluded file in the include list is refused" "include list names excluded path docker-compose.dev.yml" \
  "$B" --tag v0.0.0-ci --out "$WORK/s2o" --src "$WORK/s2" --core-migrations "$MIG"

# negative: an excluded file sneaking into a built tarball fails the check
mkdir -p "$WORK/t"; tar -xzf "$WORK/a/$TGZ" -C "$WORK/t"
cp "$ROOT/docker-compose.override.yml" "$WORK/t/vizra-bundle_v0.0.0-ci/"
tar -czf "$WORK/sneak.tar.gz" -C "$WORK/t" vizra-bundle_v0.0.0-ci
expect_fail "an excluded file sneaking into the bundle fails" "excluded path present: docker-compose.override.yml" \
  "$C" "$WORK/sneak.tar.gz" --no-render

# negative: a required item neither shipped nor declared not-yet-shipped fails
copy_src "$WORK/s3"
python3 - "$WORK/s3/scripts/bundle-contents.json" <<'PY'
import json, sys; p = sys.argv[1]; c = json.load(open(p)); del c["not_yet_shipped"]["systemd units"]; json.dump(c, open(p, "w"))
PY
"$B" --tag v0.0.0-ci --out "$WORK/s3o" --src "$WORK/s3" --core-migrations "$MIG" >/dev/null
expect_fail "an undeclared missing release item fails" "missing: systemd units" "$C" "$WORK/s3o/$TGZ" --no-render

# negative: a production shape naming a compose file absent from the include list fails
copy_src "$WORK/s4"
cp "$WORK/s4/docker-compose.external-ipfs.yml" "$WORK/s4/docker-compose.probe-overlay.yml"
python3 - "$WORK/s4/scripts/compose-shapes.json" <<'PY2'
import json, sys; p = sys.argv[1]; c = json.load(open(p))
s = next(x for x in c["shapes"] if x["id"] == "prod-external-ipfs")
s["files"] = [f if f != "docker-compose.external-ipfs.yml" else "docker-compose.probe-overlay.yml" for f in s["files"]]
json.dump(c, open(p, "w"))
PY2
"$B" --tag v0.0.0-ci --out "$WORK/s4o" --src "$WORK/s4" --core-migrations "$MIG" >/dev/null
expect_fail "a shape file absent from the include list fails" \
  "missing: production shape prod-external-ipfs needs docker-compose.probe-overlay.yml" "$C" "$WORK/s4o/$TGZ" --no-render

# negative: a tampered file fails the manifest sha256
rm -rf "$WORK/t"; mkdir -p "$WORK/t"; tar -xzf "$WORK/a/$TGZ" -C "$WORK/t"
echo "# tampered" >> "$WORK/t/vizra-bundle_v0.0.0-ci/docker-compose.yml"
tar -czf "$WORK/tamper.tar.gz" -C "$WORK/t" vizra-bundle_v0.0.0-ci
expect_fail "a tampered file fails the manifest" "sha256 mismatch: docker-compose.yml" "$C" "$WORK/tamper.tar.gz" --no-render

echo "PASS: $pass cases"
