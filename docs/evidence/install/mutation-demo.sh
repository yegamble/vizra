#!/bin/sh
# Controlled mutations of install.sh: each must turn tests/install/install_test.sh red.
# shellcheck disable=SC2016 # the mutations are literal source text
set -u
ROOT=$(cd "$(dirname "$0")/../../.." && pwd)
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
bad=0 n=0 red=0
mut() { # name python-replacement-old python-replacement-new expected-failing-test
	python3 - "$ROOT/install.sh" "$T/m.sh" "$2" "$3" <<'PY'
import sys
s=open(sys.argv[1]).read(); old=sys.argv[3]; new=sys.argv[4]
assert s.count(old)>=1, old
open(sys.argv[2],'w').write(s.replace(old,new))
PY
	out=$(INSTALL_SH="$T/m.sh" sh "$ROOT/tests/install/install_test.sh" 2>&1)
	n=$((n + 1))
	if printf '%s\n' "$out" | grep -q "^FAIL $4"; then red=$((red + 1)); echo "RED as expected: $1 -> FAIL $4"; else echo "NOT RED: $1"; bad=1; fi
}
mut skip-checksum '[ "$got" = "$2" ] ||' 'true ||' N1-checksum-mismatch
mut no-tty-check '[ -t 0 ] || die 2' 'true || die 2' N2-non-tty-refuses
mut rewrite-production-env 'say "installed into $DIR"' 'mkdir -p "$DIR/env"; echo SECRET=new >"$DIR/env/production.env"; say "installed into $DIR"' P1-production-env-untouched
mut no-resume 'done_step() { [ -f "$STATE" ] && grep -qx "$1" "$STATE"; }' 'done_step() { false; }' R1-resume-after-tree-core
mut help-needs-path "# builtins only" "cat /dev/null; # builtins only" S2-help
mut rerun-touches-state '	record cli' '	record cli
	fi; if true; then echo rerun >>"$STATE"' idempotent-second-run
mut bundle-pretends 'die 3 "no release bundle' 'GIT=1; say "no release bundle' bundle-refuses
mut state-skips-verification 'BIN=$DIR/bin/vizra
' 'BIN=$DIR/bin/vizra
if grep -q "^cli" "$STATE"; then cd "$DIR" && exec "$BIN" setup; fi
' V1-forged-state-refused
echo "mutations: $red red of $n"
exit $bad
