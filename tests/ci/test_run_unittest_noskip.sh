#!/usr/bin/env bash
# Cases for scripts/run-unittest-noskip.py: a skip, an expected failure, or an
# empty selection must fail; only a clean, non-empty suite passes.
set -u
here="$(cd "$(dirname "$0")/../.." && pwd)"
runner="$here/scripts/run-unittest-noskip.py"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
pass=0; fail=0
mk() { mkdir -p "$tmp/$1"; printf '%b' "$2" > "$tmp/$1/test_x.py"; }
run() { # name want(0|nonzero) dir args...
  local name=$1 want=$2 dir=$3; shift 3
  (cd "$tmp/$dir" && python3 "$runner" "$@") >"$tmp/out" 2>&1; rc=$?
  if { [ "$want" = 0 ] && [ "$rc" = 0 ]; } || { [ "$want" != 0 ] && [ "$rc" != 0 ]; }; then
    pass=$((pass+1)); echo "ok   $name"
  else fail=$((fail+1)); echo "FAIL $name (rc=$rc)"; sed 's/^/     /' "$tmp/out"; fi
}
H='import unittest\nclass T(unittest.TestCase):\n'
mk clean   "${H}    def test_a(self): pass\n"
mk skip    "${H}    def test_a(self): pass\n    @unittest.skip('x')\n    def test_b(self): pass\n"
mk xfail   "${H}    @unittest.expectedFailure\n    def test_a(self): self.fail()\n"
mk failing "${H}    def test_a(self): self.fail()\n"
mkdir -p "$tmp/empty"
run clean-discover   0       clean   discover -s .
run clean-module     0       clean   test_x
run skipped          nonzero skip    discover -s .
run skipped-module   nonzero skip    test_x
run expected-failure nonzero xfail   discover -s .
run failing          nonzero failing discover -s .
run empty-discover   nonzero empty   discover -s .
run no-args          nonzero clean
expected=8
echo "noskip cases: $pass passed, $fail failed (floor $expected)"
[ "$fail" = 0 ] && [ "$pass" -ge "$expected" ]
