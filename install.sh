#!/bin/sh
# Vizra installer (VZ-INSTALL-001). POSIX sh; runs under dash and busybox sh.
#
#   sh install.sh [--yes] [--ref REF] [--dir DIR] [--owner OWNER] [--git]
#                 [--cli PATH --cli-sha256 HEX]
#   (piped form: download, then feed to `sh -s -- --yes --git`)
#
# Steps, recorded one per line in DIR/.vizra-install.state so an interrupted
# run resumes at the first step not recorded:
#   docker       detect Docker + Compose >= 2.24; on Ubuntu/Debian install them
#                from Docker's official apt repository (signing-key fingerprint
#                pinned). Never Docker's convenience script.
#   tree-meta    the meta repo at --ref into DIR (--git); the release bundle
#                path refuses until a bundle is published (VZ-INSTALL-004)
#   tree-core / tree-user / tree-search   component repos at --ref (--git)
#   cli          the checksum-verified `vizra` CLI into DIR/bin/vizra
# Then hand-off: exec `vizra setup` if the CLI has it; otherwise print the next
# command and exit 0.
#
# It NEVER writes env/production.env or any secret, and never runs
# `docker compose up`.
#
# CHECKSUM MANIFEST FORMAT (bundle and CLI): sha256sum text format, one line per
# file: `<64 lowercase hex>  <file name>`. verify_sha256 compares a file
# against one hex digest; manifest_sha256 extracts the digest for a name.
#
# Exit codes: 0 ok, 1 aborted, 2 usage/refused, 3 missing dependency,
# 4 checksum failure, 75 test stop.
#
# TEST-ONLY hooks (refused unless VIZRA_INSTALL_TESTING=1):
#   VIZRA_INSTALL_TEST_STOP_AFTER=<step>  exit 75 right after <step> is recorded
#   VIZRA_INSTALL_SKIP_DOCKER=1           record the docker step without probing
#   VIZRA_INSTALL_REPO_BASE=<url>         clone from <url>/<repo>.git
set -eu

usage() {
	# builtins only: --help must work with an empty PATH (S2)
	printf '%s\n' \
		'Usage: install.sh [options]' \
		'' \
		'  --yes              do not ask; required when stdin is not a terminal' \
		'  --ref REF          release tag or branch to install (default: main)' \
		'  --dir DIR          install directory (default: /opt/vizra)' \
		'  --owner OWNER      GitHub owner of the vizra repos (default: yegamble)' \
		'  --git              clone the meta + vizra-core, vizra-user, vizra-search repos' \
		'                     instead of unpacking the release bundle' \
		'  --cli PATH         use this local vizra CLI binary ...' \
		'  --cli-sha256 HEX   ... which must match this sha256 (required with --cli)' \
		'  -h, --help         show this help and exit' \
		'' \
		'Never writes env/production.env or any secret; never runs docker compose up.' \
		'Hands over to: vizra setup'
}

die() { code=$1; shift; printf 'install.sh: %s\n' "$*" >&2; exit "$code"; }
say() { printf '==> %s\n' "$*"; }

YES=0 REF=main DIR=/opt/vizra OWNER=yegamble GIT=0 CLI='' CLI_SHA=''
while [ $# -gt 0 ]; do
	case $1 in
	-h|--help) usage; exit 0 ;;
	--yes|-y) YES=1 ;;
	--git) GIT=1 ;;
	--ref|--dir|--owner|--cli|--cli-sha256)
		[ $# -ge 2 ] || die 2 "$1 needs a value"
		case $1 in
		--ref) REF=$2 ;;
		--dir) DIR=$2 ;;
		--owner) OWNER=$2 ;;
		--cli) CLI=$2 ;;
		--cli-sha256) CLI_SHA=$2 ;;
		esac
		shift ;;
	*) die 2 "unknown option: $1 (see --help)" ;;
	esac
	shift
done

if [ "${VIZRA_INSTALL_TESTING:-}" != 1 ]; then
	for v in VIZRA_INSTALL_TEST_STOP_AFTER VIZRA_INSTALL_SKIP_DOCKER VIZRA_INSTALL_REPO_BASE; do
		eval "val=\${$v:-}"
		[ -z "$val" ] || die 2 "$v is a test-only hook; refused without VIZRA_INSTALL_TESTING=1"
	done
fi

case $REF in ''|-*|*[!A-Za-z0-9._/-]*) die 2 "invalid --ref: $REF" ;; esac
case $OWNER in ''|-*|*[!A-Za-z0-9-]*) die 2 "invalid --owner: $OWNER" ;; esac
case $DIR in /*) ;; *) die 2 "--dir must be an absolute path" ;; esac
if [ -n "$CLI" ] || [ -n "$CLI_SHA" ]; then
	{ [ -n "$CLI" ] && [ -n "$CLI_SHA" ]; } || die 2 "--cli and --cli-sha256 go together"
fi

# N2: never act unattended without consent.
if [ "$YES" != 1 ]; then
	[ -t 0 ] || die 2 "stdin is not a terminal; re-run with --yes to install unattended"
	printf 'Install Vizra %s into %s? [y/N] ' "$REF" "$DIR"
	read -r ans || ans=''
	case $ans in y|Y|yes|YES) ;; *) die 1 "aborted" ;; esac
fi

sha256_of() {
	if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | cut -d' ' -f1
	elif command -v shasum >/dev/null 2>&1; then shasum -a 256 "$1" | cut -d' ' -f1
	else die 3 "need sha256sum or shasum"; fi
}

# verify_sha256 FILE HEX: abort (exit 4) unless FILE's sha256 is exactly HEX.
verify_sha256() {
	case $2 in ''|*[!0-9a-f]*) die 4 "malformed sha256 for $1" ;; esac
	[ ${#2} -eq 64 ] || die 4 "malformed sha256 for $1"
	got=$(sha256_of "$1")
	[ "$got" = "$2" ] || die 4 "checksum mismatch for $1: expected $2, got $got; nothing written"
}

# manifest_sha256 MANIFEST NAME: print the digest recorded for NAME.
# Used by the bundle path once a bundle is published (VZ-INSTALL-004).
# shellcheck disable=SC2329
manifest_sha256() {
	awk -v n="$2" '$2 == n || $2 == "*" n { print $1; exit }' "$1"
}

# Everything checkable without writing is checked first (N1).
if [ -n "$CLI" ]; then
	[ -f "$CLI" ] || die 2 "--cli $CLI is not a file"
	verify_sha256 "$CLI" "$CLI_SHA"
fi
if [ "$GIT" != 1 ]; then
	# A bundle would be fetched with its manifest and checked via
	# manifest_sha256 + verify_sha256 before unpacking (VZ-INSTALL-004).
	die 3 "no release bundle is published for $REF; use --git"
fi
command -v git >/dev/null 2>&1 || die 3 "git is required for --git"

STATE=$DIR/.vizra-install.state
done_step() { [ -f "$STATE" ] && grep -qx "$1" "$STATE"; }
record() {
	printf '%s\n' "$1" >>"$STATE"
	if [ "${VIZRA_INSTALL_TEST_STOP_AFTER:-}" = "$1" ]; then
		say "test hook: stopping after $1"
		exit 75
	fi
}

compose_ok() {
	v=$(docker compose version --short 2>/dev/null) || return 1
	v=${v#v}; maj=${v%%.*}; rest=${v#*.}; min=${rest%%.*}
	case $maj$min in ''|*[!0-9]*) return 1 ;; esac
	[ "$maj" -gt 2 ] || { [ "$maj" -eq 2 ] && [ "$min" -ge 24 ]; }
}

DOCKER_FPR=9DC858229FC7DD38854AE2D88D81803C0EBFCD88
install_docker() {
	[ "$(id -u)" -eq 0 ] || die 3 "Docker + Compose >= 2.24 missing; re-run as root to install them"
	[ -r /etc/os-release ] || die 3 "unknown platform; install Docker + Compose >= 2.24 yourself"
	# shellcheck disable=SC1091
	. /etc/os-release
	case $ID in ubuntu|debian) ;; *) die 3 "unsupported platform $ID; install Docker + Compose >= 2.24 yourself" ;; esac
	export DEBIAN_FRONTEND=noninteractive
	apt-get update -q
	apt-get install -y -q ca-certificates curl gnupg
	install -m 0755 -d /etc/apt/keyrings
	tmpk=$(mktemp)
	curl -fsSL "https://download.docker.com/linux/$ID/gpg" -o "$tmpk"
	fpr=$(gpg --show-keys --with-colons "$tmpk" | awk -F: '$1=="fpr"{print $10; exit}')
	[ "$fpr" = "$DOCKER_FPR" ] || { rm -f "$tmpk"; die 4 "Docker apt key fingerprint $fpr != pinned $DOCKER_FPR"; }
	gpg --dearmor <"$tmpk" >/etc/apt/keyrings/docker.gpg
	rm -f "$tmpk"
	printf 'deb [arch=%s signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/%s %s stable\n' \
		"$(dpkg --print-architecture)" "$ID" "$VERSION_CODENAME" >/etc/apt/sources.list.d/docker.list
	apt-get update -q
	apt-get install -y -q docker-ce docker-ce-cli containerd.io docker-compose-plugin
}

clone_at() { # URL DEST
	mkdir -p "$2"
	[ -d "$2/.git" ] || git -C "$2" init -q
	git -C "$2" fetch -q --depth 1 "$1" "$REF"
	git -C "$2" -c advice.detachedHead=false checkout -q --detach FETCH_HEAD
}

BASE=${VIZRA_INSTALL_REPO_BASE:-https://github.com/$OWNER}
mkdir -p "$DIR"

if ! done_step docker; then
	if [ "${VIZRA_INSTALL_SKIP_DOCKER:-}" != 1 ]; then
		{ command -v docker >/dev/null 2>&1 && compose_ok; } || install_docker
		compose_ok || die 3 "docker compose >= 2.24 is required"
	fi
	record docker
fi
for r in meta core user search; do
	done_step "tree-$r" && continue
	if [ "$r" = meta ]; then clone_at "$BASE/vizra.git" "$DIR"
	else clone_at "$BASE/vizra-$r.git" "$DIR/vizra-$r"; fi
	record "tree-$r"
done
if ! done_step cli; then
	[ -n "$CLI" ] || die 3 "no checksum-verified vizra CLI is published for $REF; pass --cli PATH --cli-sha256 HEX (tree is in place; a re-run resumes here)"
	mkdir -p "$DIR/bin"
	cp "$CLI" "$DIR/bin/vizra.tmp"
	chmod 0755 "$DIR/bin/vizra.tmp"
	verify_sha256 "$DIR/bin/vizra.tmp" "$CLI_SHA"
	mv "$DIR/bin/vizra.tmp" "$DIR/bin/vizra"
	record cli
fi

say "installed into $DIR"
cd "$DIR"
if "$DIR/bin/vizra" setup --help >/dev/null 2>&1; then
	exec "$DIR/bin/vizra" setup
fi
say "this vizra CLI has no 'setup' command yet (VZ-INSTALL-002); the interview did not start."
say "next: cd $DIR && $DIR/bin/vizra setup"
exit 0
