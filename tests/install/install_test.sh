#!/bin/sh
# VZ-INSTALL-001 installer tests. POSIX sh, no network: every clone comes from
# local bare repos built under a mktemp dir. Usage: sh tests/install/install_test.sh
# INSTALL_SH=<path> runs the suite against another copy (mutation demos).
set -u
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
INSTALL_SH=${INSTALL_SH:-$ROOT/install.sh}
W=$(mktemp -d)
trap 'rm -rf "$W"' EXIT
pass=0 fail=0
ok() { pass=$((pass + 1)); printf 'ok   %s\n' "$1"; }
no() { fail=$((fail + 1)); printf 'FAIL %s\n' "$1"; }
sha() { if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | cut -d' ' -f1; else shasum -a 256 "$1" | cut -d' ' -f1; fi; }
treesum() { # digest of every path + content under $1, excluding .git internals
	(cd "$1" && find . -path '*/.git' -prune -o -type f -print | LC_ALL=C sort | while read -r f; do printf '%s %s\n' "$f" "$(sha "$f")"; done; \
	 for g in . vizra-core vizra-user vizra-search; do [ -d "$g/.git" ] && git -C "$g" rev-parse HEAD; done) | cksum
}

# fixtures: four bare repos with a main branch
for r in vizra vizra-core vizra-user vizra-search; do
	git init -q "$W/src/$r"
	echo "$r" >"$W/src/$r/README"
	git -C "$W/src/$r" add README
	git -C "$W/src/$r" -c user.name=t -c user.email=t@t commit -q -m init
	git -C "$W/src/$r" branch -M main
	git clone -q --bare "$W/src/$r" "$W/repos/$r.git"
done
printf '#!/bin/sh\necho fixture-cli\nexit 1\n' >"$W/vizra-cli"
CLI_SHA=$(sha "$W/vizra-cli")
BAD=0000000000000000000000000000000000000000000000000000000000000000

run() { # DIR args... ; stdin is /dev/null
	d=$1; shift
	VIZRA_INSTALL_TESTING=1 VIZRA_INSTALL_SKIP_DOCKER=1 VIZRA_INSTALL_REPO_BASE="file://$W/repos" \
		sh "$INSTALL_SH" --dir "$d" "$@" </dev/null >"$W/out" 2>&1
}
full() { fd=$1; shift; run "$fd" --yes --git --cli "$W/vizra-cli" --cli-sha256 "$CLI_SHA" "$@"; }

# S2: --help with no network, no root, no clone, minimal PATH, under /bin/sh
mkdir -p "$W/s2"
if (cd "$W/s2" && env -i PATH=/nonexistent HOME="$W/s2" /bin/sh "$INSTALL_SH" --help >"$W/out" 2>&1) \
	&& grep -q -- '--cli-sha256' "$W/out" && [ -z "$(ls -A "$W/s2")" ]; then ok S2-help; else no S2-help; fi

# N2: no tty, no --yes -> exit 2, nothing created
run "$W/n2" --git --cli "$W/vizra-cli" --cli-sha256 "$CLI_SHA"; rc=$?
if [ $rc -eq 2 ] && [ ! -e "$W/n2" ]; then ok N2-non-tty-refuses; else no "N2-non-tty-refuses (rc=$rc)"; fi

# N1: wrong sha256 aborts before writing; existing dir unchanged
mkdir -p "$W/n1"; echo keep >"$W/n1/marker"; before=$(treesum "$W/n1")
run "$W/n1" --yes --git --cli "$W/vizra-cli" --cli-sha256 "$BAD"; rc=$?
if [ $rc -eq 4 ] && [ "$(treesum "$W/n1")" = "$before" ] && [ "$(ls -A "$W/n1")" = marker ]; then ok N1-checksum-mismatch; else no "N1-checksum-mismatch (rc=$rc)"; fi

# bundle path refuses honestly
run "$W/bun" --yes; rc=$?
if [ $rc -eq 3 ] && grep -q 'no release bundle is published for main; use --git' "$W/out" && [ ! -e "$W/bun" ]; then ok bundle-refuses; else no "bundle-refuses (rc=$rc)"; fi

# --git path: full tree + CLI + hand-off message
full "$W/a"; rc=$?
if [ $rc -eq 0 ] && [ -f "$W/a/README" ] && [ -f "$W/a/vizra-core/README" ] && [ -f "$W/a/vizra-user/README" ] \
	&& [ -f "$W/a/vizra-search/README" ] && [ -x "$W/a/bin/vizra" ] && grep -q "next: cd $W/a && $W/a/bin/vizra setup" "$W/out"; then
	ok git-path-tree-cli-handoff; else no "git-path-tree-cli-handoff (rc=$rc)"; cat "$W/out"; fi

# no CLI -> stops before hand-off, non-zero
run "$W/nocli" --yes --git; rc=$?
if [ $rc -eq 3 ] && grep -q 'no checksum-verified vizra CLI' "$W/out" && ! grep -q 'next:' "$W/out"; then ok no-cli-stops; else no "no-cli-stops (rc=$rc)"; fi

# idempotence: second run changes nothing (tree + state file)
t1=$(treesum "$W/a"); s1=$(sha "$W/a/.vizra-install.state")
full "$W/a"; rc=$?
if [ $rc -eq 0 ] && [ "$(treesum "$W/a")" = "$t1" ] && [ "$(sha "$W/a/.vizra-install.state")" = "$s1" ]; then ok idempotent-second-run; else no "idempotent-second-run (rc=$rc)"; fi

# P1: existing env/production.env is byte-identical afterwards (fresh + rerun)
mkdir -p "$W/p/env"; printf 'SECRET=keep-me\n' >"$W/p/env/production.env"; p0=$(sha "$W/p/env/production.env")
full "$W/p"; rc1=$?; full "$W/p"; rc2=$?
if [ $rc1 -eq 0 ] && [ $rc2 -eq 0 ] && [ "$(sha "$W/p/env/production.env")" = "$p0" ]; then ok P1-production-env-untouched; else no "P1-production-env-untouched ($rc1/$rc2)"; fi
if [ ! -e "$W/a/env/production.env" ]; then ok P1-never-creates-production-env; else no P1-never-creates-production-env; fi

# R1: stop after each step k, rerun resumes at k+1, final tree == uninterrupted
for k in docker tree-meta tree-core tree-user tree-search; do
	d="$W/r-$k"
	VIZRA_INSTALL_TEST_STOP_AFTER=$k full "$d"; rc=$?
	last=$(tail -n 1 "$d/.vizra-install.state" 2>/dev/null)
	full "$d"; rc2=$?
	n=$(grep -c . "$d/.vizra-install.state")
	if [ $rc -eq 75 ] && [ "$last" = "$k" ] && [ $rc2 -eq 0 ] && [ "$n" -eq 6 ] \
		&& [ "$(cd "$d" && treesum .)" = "$(cd "$W/a" && treesum .)" ] \
		&& [ "$(sha "$d/.vizra-install.state")" = "$s1" ]; then ok "R1-resume-after-$k"; else no "R1-resume-after-$k ($rc/$rc2/$n)"; fi
done

# V1 (fix round 1): a forged state file listing every step plus an unverified
# bin/vizra must not make the installer run that binary, even with a valid --cli.
f="$W/forged"; mkdir -p "$f/bin"
printf 'docker\ntree-meta\ntree-core\ntree-user\ntree-search\ncli\n' >"$f/.vizra-install.state"
printf '#!/bin/sh\necho EVIL-UNVERIFIED "$@"\nexit 0\n' >"$f/bin/vizra"; chmod 0755 "$f/bin/vizra"
full "$f"; rc=$?
if [ $rc -ne 0 ] && ! grep -q EVIL-UNVERIFIED "$W/out"; then ok V1-forged-state-refused; else no "V1-forged-state-refused (rc=$rc)"; cat "$W/out"; fi

# V2: a correct state file with a tampered bin/vizra is refused, binary never run
cp -R "$W/a" "$W/tamper"
printf '#!/bin/sh\necho EVIL-TAMPERED "$@"\nexit 0\n' >"$W/tamper/bin/vizra"
full "$W/tamper"; rc=$?
if [ $rc -ne 0 ] && ! grep -q EVIL-TAMPERED "$W/out"; then ok V2-tampered-cli-refused; else no "V2-tampered-cli-refused (rc=$rc)"; cat "$W/out"; fi
run "$W/tamper" --yes --git; rc=$?
if [ $rc -eq 3 ] && ! grep -q EVIL-TAMPERED "$W/out"; then ok V2-no-checksum-no-exec; else no "V2-no-checksum-no-exec (rc=$rc)"; fi

# V3: a re-run with a NEW valid --cli/--cli-sha256 replaces the binary and hands over to it
cp -R "$W/a" "$W/up"
# shellcheck disable=SC2016 # literal script text
printf '#!/bin/sh\nif [ "$1 $2" = "setup --help" ]; then exit 0; fi\necho NEW-CLI-RAN "$@"\nexit 0\n' >"$W/cli2"
run "$W/up" --yes --git --cli "$W/cli2" --cli-sha256 "$(sha "$W/cli2")"; rc=$?
if [ $rc -eq 0 ] && grep -q 'NEW-CLI-RAN setup' "$W/out" && [ "$(sha "$W/up/bin/vizra")" = "$(sha "$W/cli2")" ] \
	&& grep -qx "cli $(sha "$W/cli2")" "$W/up/.vizra-install.state" && [ ! -e "$W/up/bin/vizra.tmp" ]; then
	ok V3-upgrade-replaces-cli; else no "V3-upgrade-replaces-cli (rc=$rc)"; cat "$W/out"; fi

# test hooks are refused outside test mode
VIZRA_INSTALL_TEST_STOP_AFTER=docker sh "$INSTALL_SH" --yes --git --dir "$W/hook" </dev/null >"$W/out" 2>&1; rc=$?
if [ $rc -eq 2 ] && [ ! -e "$W/hook" ]; then ok test-hook-refused; else no "test-hook-refused (rc=$rc)"; fi

printf '%d passed, %d failed\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
