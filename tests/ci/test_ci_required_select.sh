#!/usr/bin/env bash
# Regression cases for scripts/ci-required-select.sh (VZ-CI-001 R1, N1, S2).
set -uo pipefail
here="$(cd "$(dirname "$0")/../.." && pwd)"
sel="$here/scripts/ci-required-select.sh"
pass=0; fail=0
t="$(printf '\t')"
run() { # name want_rc want_text required tsv
  out="$(printf '%b' "$5" | "$sel" "$4" 2>&1)"; rc=$?
  if [ "$rc" = "$2" ] && printf '%s' "$out" | grep -qF "$3"; then pass=$((pass+1)); echo "ok   $1"
  else fail=$((fail+1)); echo "FAIL $1 (rc=$rc want $2 '$3')"; printf '%s\n' "$out" | sed 's/^/     /'; fi
}
ok="validate${t}completed${t}success${t}2026-11-12T00:00:00Z\n"
run all-success          0 "validate: success"   validate "$ok"
run empty-selection      2 "validate: NEVER RAN" validate ""
run omitted-lane         2 "boot: NEVER RAN"     "$(printf 'validate\nboot')" "$ok"
run renamed-job          2 "validate: NEVER RAN" validate "validate-v2${t}completed${t}success${t}2026-11-12T00:00:00Z\n"
run skipped              1 "validate: skipped"   validate "validate${t}completed${t}skipped${t}2026-11-12T00:00:00Z\n"
run cancelled            1 "validate: cancelled" validate "validate${t}completed${t}cancelled${t}2026-11-12T00:00:00Z\n"
run timed-out            1 "validate: timed_out" validate "validate${t}completed${t}timed_out${t}2026-11-12T00:00:00Z\n"
run neutral              1 "validate: neutral"   validate "validate${t}completed${t}neutral${t}2026-11-12T00:00:00Z\n"
run stale-success-masks  1 "AMBIGUOUS"           validate "validate${t}completed${t}success${t}2026-11-11T00:00:00Z\nvalidate${t}completed${t}failure${t}2026-11-12T00:00:00Z\n"
run pending              2 "validate: in_progress" validate "validate${t}in_progress${t}none${t}2026-11-12T00:00:00Z\n"
# An empty required list is a usage error, never a pass.
out="$(printf '' | "$sel" "" 2>&1)"; rc=$?
if [ "$rc" != 0 ]; then pass=$((pass+1)); echo "ok   empty-required"; else fail=$((fail+1)); echo "FAIL empty-required passed"; fi
expected=11
echo "select cases: $pass passed, $fail failed (floor $expected)"
[ "$fail" = 0 ] && [ "$pass" -ge "$expected" ]
