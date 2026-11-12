#!/usr/bin/env bash
# Regression cases for scripts/check-required-tombstones.sh (VZ-CI-001 S1, R1).
# Each case writes a base and a head manifest and asserts the exit code and,
# for rejections, the named reason. Run by the required `ci-required` lane.
set -uo pipefail
here="$(cd "$(dirname "$0")/../.." && pwd)"
chk="$here/scripts/check-required-tombstones.sh"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
pass=0; fail=0
run() { # name want_rc want_text base head
  printf '%b' "$4" > "$tmp/base"; printf '%b' "$5" > "$tmp/head"
  out="$("$chk" --base-file "$tmp/base" --head-file "$tmp/head" 2>&1)"; rc=$?
  if [ "$rc" = "$2" ] && { [ -z "$3" ] || printf '%s' "$out" | grep -qF "$3"; }; then
    pass=$((pass+1)); echo "ok   $1"
  else
    fail=$((fail+1)); echo "FAIL $1 (rc=$rc want $2 '$3')"; printf '%s\n' "$out" | sed 's/^/     /'
  fi
}
T='# tombstone: bundle retired 2026-11-12 because replaced by boot'
run unchanged                0 ""                          'validate\nbundle\n' 'validate\nbundle\n'
run add-lane                 0 ""                          'validate\n' 'validate\nbundle\n'
run removed-no-tombstone     1 "REMOVED WITHOUT TOMBSTONE: bundle" 'validate\nbundle\n' 'validate\n'
run commented-out            1 "REMOVED WITHOUT TOMBSTONE: bundle" 'validate\nbundle\n' 'validate\n# bundle\n'
run removed-with-tombstone   0 ""                          'validate\nbundle\n' "validate\n$T\n"
run tombstone-no-date        1 "MALFORMED TOMBSTONE"       'validate\nbundle\n' 'validate\n# tombstone: bundle retired because x\n'
run tombstone-bad-date       1 "MALFORMED TOMBSTONE"       'validate\nbundle\n' 'validate\n# tombstone: bundle retired 2026-13-40 because x\n'
run tombstone-no-reason      1 "MALFORMED TOMBSTONE"       'validate\nbundle\n' 'validate\n# tombstone: bundle retired 2026-11-12 because \n'
run tombstone-unknown-lane   1 "BASE NEVER HAD: ghost"     'validate\n' 'validate\n# tombstone: ghost retired 2026-11-12 because x\n'
run tombstone-still-listed   1 "STILL LISTED: bundle"      'validate\nbundle\n' "validate\nbundle\n$T\n"
run tombstone-floor-lane     1 "FLOOR LANE: validate"      'validate\nbundle\n' 'bundle\n# tombstone: validate retired 2026-11-12 because x\n'
run earlier-tombstone-kept   0 ""                          "validate\n$T\n" "validate\n$T\n"
run earlier-tombstone-deleted 1 "TOMBSTONE DELETED: bundle" "validate\n$T\n" 'validate\n'
run renamed-lane             1 "REMOVED WITHOUT TOMBSTONE: bundle" 'validate\nbundle\n' 'validate\nbundles\n'
run empty-head               1 "REMOVED WITHOUT TOMBSTONE: validate" 'validate\n' '# nothing\n'
# Base unavailable fails closed (no --base-file, bogus SHA).
out="$(cd "$here" && BASE_SHA=0000000000000000000000000000000000000000 "$chk" 2>&1)"; rc=$?
if [ "$rc" = 1 ] && printf '%s' "$out" | grep -qF "BASE MANIFEST UNAVAILABLE"; then pass=$((pass+1)); echo "ok   base-unavailable"
else fail=$((fail+1)); echo "FAIL base-unavailable (rc=$rc)"; printf '%s\n' "$out"; fi
expected=16
echo "tombstone cases: $pass passed, $fail failed (floor $expected)"
[ "$fail" = 0 ] && [ "$pass" -ge "$expected" ]
