#!/bin/sh
# bootstrap.sh — clone or update the nested component checkouts (VZ-FOUND-001).
#
#   VIZRA_REF=<tag|branch|sha> ./bootstrap.sh   # every component detached at that ref
#   ./bootstrap.sh                              # every component on its default branch
#
# Environment:
#   VIZRA_REF        ref to pin in every component (optional)
#   VIZRA_OWNER      GitHub owner (default: yegamble)
#   VIZRA_REPO_BASE  remote base URL (default: https://github.com/$VIZRA_OWNER)
#   VIZRA_DIR        directory holding the checkouts (default: this script's dir)
#
# Idempotent: a rerun fetches and verifies HEAD; it never resets, stashes or
# discards local work. A dirty checkout is refused with a non-zero exit.
set -eu

COMPONENTS="vizra-core vizra-user vizra-search"
VIZRA_OWNER="${VIZRA_OWNER:-yegamble}"
VIZRA_REF="${VIZRA_REF:-}"
VIZRA_DIR="${VIZRA_DIR:-$(cd "$(dirname "$0")" && pwd)}"

die() { echo "bootstrap: $*" >&2; exit 1; }

case "$VIZRA_OWNER" in
  ''|-*|*[!A-Za-z0-9_.-]*) die "refusing VIZRA_OWNER '$VIZRA_OWNER': only [A-Za-z0-9_.-]" ;;
esac
VIZRA_REPO_BASE="${VIZRA_REPO_BASE:-https://github.com/$VIZRA_OWNER}"

if [ -n "$VIZRA_REF" ]; then
  case "$VIZRA_REF" in
    -*|*..*|*[!A-Za-z0-9_./-]*)
      die "refusing VIZRA_REF '$VIZRA_REF': only [A-Za-z0-9_./-], no leading '-' or '..'" ;;
  esac
  echo "bootstrap: VIZRA_REF=$VIZRA_REF — every component detached at that ref"
else
  echo "bootstrap: VIZRA_REF unset — every component on its remote default branch (not pinned)"
fi

# resolve <dir> <ref>: remote branch first, then tag/sha.
resolve() {
  git -C "$1" rev-parse -q --verify "refs/remotes/origin/$2^{commit}" 2>/dev/null ||
    git -C "$1" rev-parse -q --verify "refs/tags/$2^{commit}" 2>/dev/null ||
    git -C "$1" rev-parse -q --verify "$2^{commit}" 2>/dev/null ||
    die "$(basename "$1"): ref '$2' not found"
}

# Preflight every existing checkout BEFORE touching any, so a refusal leaves
# the whole set exactly as it was.
for c in $COMPONENTS; do
  dir="$VIZRA_DIR/$c"
  [ -e "$dir" ] || continue
  [ -d "$dir/.git" ] || [ -f "$dir/.git" ] || die "$c: $dir exists but is not a git checkout"
  if [ -n "$(git -C "$dir" status --porcelain)" ]; then
    die "$c: checkout at $dir has local changes; refusing to touch it (commit or move them, then rerun)"
  fi
done

for c in $COMPONENTS; do
  dir="$VIZRA_DIR/$c"
  url="$VIZRA_REPO_BASE/$c.git"
  if [ ! -e "$dir" ]; then
    git clone -q -- "$url" "$dir"
  else
    git -C "$dir" fetch -q --tags origin
  fi

  if [ -n "$VIZRA_REF" ]; then
    want="$(resolve "$dir" "$VIZRA_REF")"
    if [ "$(git -C "$dir" rev-parse HEAD)" != "$want" ] || git -C "$dir" symbolic-ref -q HEAD >/dev/null; then
      git -C "$dir" checkout -q --detach "$want"
    fi
  else
    git -C "$dir" remote set-head origin --auto >/dev/null 2>&1 || true
    def="$(git -C "$dir" symbolic-ref -q --short refs/remotes/origin/HEAD)" ||
      die "$c: cannot determine the remote default branch"
    branch="${def#origin/}"
    if [ "$(git -C "$dir" symbolic-ref -q --short HEAD || true)" != "$branch" ]; then
      git -C "$dir" checkout -q "$branch"
    fi
    if [ "$(git -C "$dir" rev-parse HEAD)" != "$(git -C "$dir" rev-parse "$def")" ]; then
      git -C "$dir" merge -q --ff-only "$def" ||
        die "$c: $branch has diverged from $def; refusing to reset it"
    fi
  fi
  printf 'bootstrap: %-13s %s %s\n' "$c" "$(git -C "$dir" rev-parse HEAD)" \
    "$(git -C "$dir" symbolic-ref -q --short HEAD || echo '(detached)')"
done
