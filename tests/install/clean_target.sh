#!/bin/sh
# VZ-INSTALL-001 clean target: run install.sh inside a digest-pinned
# ubuntu:24.04 (real /bin/sh = dash), as root and as the non-root `ubuntu` user.
#   1. --help with --network none exits 0 and writes nothing (S2).
#   2. --git --skip-docker against the GitHub repos without --cli exits 3 with
#      the honest "no CLI published" message and the tree in place.
#   3. Re-run with a PLACEHOLDER local CLI (a script that implements no
#      command; no vizra CLI is published yet) exits 0 and names the
#      `vizra setup` hand-off (S1 stays open: setup does not exist).
#   4. A third run changes nothing (tree listing + state file sha256 equal).
# Docker itself is skipped (--skip-docker): installing Docker inside a
# container is not this check. --ref is `main` because --ref applies to all
# four repos; a meta-only SHA does not exist in the component repos.
set -eu
IMAGE=ubuntu:24.04@sha256:2198e4c65076e9cb0b3d695219df667c0e3b0072da64ca3c2648aca17dcecaf5
REF=${VZ_CLEAN_REF:-main}
here=$(cd "$(dirname "$0")/../.." && pwd)

for u in root ubuntu; do
	echo "== --help, --network none, user $u"
	docker run --rm --network none --user "$u" -v "$here/install.sh:/src/install.sh:ro" "$IMAGE" sh -euc '
		readlink -f /bin/sh
		touch /tmp/.m; sleep 1
		sh /src/install.sh --help | grep -q "vizra setup"
		w=$(find / -xdev -newer /tmp/.m ! -path "/proc/*" ! -path "/sys/*" ! -path "/dev/*" 2>/dev/null | grep -v "^/tmp/.m$" || true)
		[ -z "$w" ] || { echo "--help wrote: $w"; exit 1; }
		echo "help ok: exit 0, nothing written"'
done

docker run --rm -e REF="$REF" -v "$here/install.sh:/src/install.sh:ro" "$IMAGE" sh -euc '
	apt-get update -qq >/dev/null && apt-get install -y -qq git ca-certificates >/dev/null
	cat >/tmp/cli <<"C"
#!/bin/sh
echo "placeholder CLI: no commands" >&2; exit 64
C
	chmod 0755 /tmp/cli
	SUM=$(sha256sum /tmp/cli | cut -d" " -f1)
	run_as() { if [ "$1" = root ]; then shift; sh -c "$*"; else shift; su ubuntu -s /bin/sh -c "$*"; fi; }
	for u in root ubuntu; do
		D=/tmp/vz-target-$u
		echo "== full run, user $u, dir $D, ref $REF"
		set +e; out=$(run_as $u sh /src/install.sh --yes --git --skip-docker --ref "$REF" --dir $D 2>&1); rc=$?; set -e
		echo "$out"; [ $rc -eq 3 ] || { echo "expected exit 3 without --cli, got $rc"; exit 1; }
		echo "$out" | grep -q "no checksum-verified vizra CLI" || exit 1
		for t in . vizra-core vizra-user vizra-search; do [ -d $D/$t/.git ] || { echo "missing $D/$t"; exit 1; }; done
		[ ! -e $D/env/production.env ] || { echo "production.env written"; exit 1; }
		out=$(run_as $u sh /src/install.sh --yes --git --skip-docker --ref "$REF" --dir $D --cli /tmp/cli --cli-sha256 $SUM 2>&1)
		echo "$out"
		echo "$out" | grep -q "next: cd $D && $D/bin/vizra setup" || exit 1
		snap() { (cd $D && find . -path "*/.git" -prune -o -print | LC_ALL=C sort | sha256sum; sha256sum .vizra-install.state; git -c safe.directory="*" -C $D rev-parse HEAD); }
		a=$(snap)
		run_as $u sh /src/install.sh --yes --git --skip-docker --ref "$REF" --dir $D --cli /tmp/cli --cli-sha256 $SUM >/dev/null 2>&1
		b=$(snap)
		echo "$a"; [ "$a" = "$b" ] || { echo "second run changed the tree"; echo "$b"; exit 1; }
		echo "idempotent ok ($u)"
	done
	echo "clean target: all checks passed"'
