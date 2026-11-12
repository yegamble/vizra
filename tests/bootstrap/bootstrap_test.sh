#!/bin/sh
# VZ-FOUND-001 bootstrap.sh tests, against local bare repos (no network).
# BOOTSTRAP may point at an alternative script (mutation demos).
set -eu
here="$(cd "$(dirname "$0")/../.." && pwd)"
BOOTSTRAP="${BOOTSTRAP:-$here/bootstrap.sh}"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
export GIT_CONFIG_GLOBAL=/dev/null GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t \
  GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t
fails=0; passes=0
ok() { passes=$((passes + 1)); echo "PASS $1"; }
bad() { fails=$((fails + 1)); echo "FAIL $1"; }

# One history, three bare remotes: a single VIZRA_REF sha exists in every component.
git init -q -b main "$tmp/src"
echo one > "$tmp/src/f"; git -C "$tmp/src" add f; git -C "$tmp/src" commit -qm one
echo two > "$tmp/src/f"; git -C "$tmp/src" commit -qam two
for c in vizra-core vizra-user vizra-search; do git clone -q --bare "$tmp/src" "$tmp/remotes/$c.git"; done
old_sha=$(git -C "$tmp/src" rev-parse HEAD~1)
# run <dir> [ref] — the ref is an argument: `VAR=x func` persists in POSIX sh.
run() { VIZRA_REF="${2:-}" VIZRA_REPO_BASE="file://$tmp/remotes" VIZRA_DIR="$1" sh "$BOOTSTRAP"; }
state() { for c in vizra-core vizra-user vizra-search; do
  git -C "$1/$c" rev-parse HEAD; git -C "$1/$c" symbolic-ref -q HEAD || echo detached
  git -C "$1/$c" status --porcelain; (cd "$1/$c" && find . -path ./.git -prune -o -type f -print | sort | xargs cat)
done | shasum -a 256; }

# S2: clean run clones all three on the default branch.
mkdir "$tmp/a"
if run "$tmp/a" >"$tmp/out" 2>&1 && [ "$(git -C "$tmp/a/vizra-user" symbolic-ref --short HEAD)" = main ] \
  && [ -d "$tmp/a/vizra-core/.git" ] && [ -d "$tmp/a/vizra-search/.git" ]; then ok S2-clone; else bad S2-clone; cat "$tmp/out"; fi

# S2: VIZRA_REF=<sha> pins every component detached at that sha.
mkdir "$tmp/b"
if run "$tmp/b" "$old_sha" >"$tmp/out" 2>&1 && for c in vizra-core vizra-user vizra-search; do
     [ "$(git -C "$tmp/b/$c" rev-parse HEAD)" = "$old_sha" ] && ! git -C "$tmp/b/$c" symbolic-ref -q HEAD >/dev/null || exit 1
   done && grep -q "$old_sha" "$tmp/out"; then ok S2-ref-detached; else bad S2-ref-detached; cat "$tmp/out"; fi
# a tag pins too
for c in vizra-core vizra-user vizra-search; do git -C "$tmp/remotes/$c.git" tag v0.0.1 "$old_sha"; done
mkdir "$tmp/t"
if run "$tmp/t" v0.0.1 >/dev/null 2>&1 && [ "$(git -C "$tmp/t/vizra-search" rev-parse HEAD)" = "$old_sha" ]; then ok S2-tag; else bad S2-tag; fi

# R1: rerun is a no-op (default branch and pinned).
before=$(state "$tmp/a"); run "$tmp/a" >"$tmp/out" 2>&1 || cat "$tmp/out"; after=$(state "$tmp/a")
if [ "$before" = "$after" ]; then ok R1-rerun-default; else bad R1-rerun-default; fi
before=$(state "$tmp/t"); run "$tmp/t" v0.0.1 >/dev/null 2>&1; after=$(state "$tmp/t")
if [ "$before" = "$after" ]; then ok R1-rerun-pinned; else bad R1-rerun-pinned; fi

# Dirty checkout: refused, non-zero, work untouched.
echo local-work > "$tmp/t/vizra-user/f"
before=$(state "$tmp/t")
if run "$tmp/t" >"$tmp/out" 2>&1; then bad dirty-refused; else
  after=$(state "$tmp/t")
  if [ "$before" = "$after" ] && grep -q 'local changes' "$tmp/out" && [ "$(cat "$tmp/t/vizra-user/f")" = local-work ]; then ok dirty-refused; else bad dirty-refused; cat "$tmp/out"; fi
fi

# Bad refs refused before any clone.
# shellcheck disable=SC2016 # literal metacharacters are the point
for r in 'main;id' '$(id)' '-x' 'a..b' 'a b'; do
  mkdir "$tmp/bad"
  if run "$tmp/bad" "$r" >"$tmp/out" 2>&1; then bad "bad-ref:$r"
  elif [ -z "$(ls -A "$tmp/bad")" ] && grep -q refusing "$tmp/out"; then ok "bad-ref:$r"; else bad "bad-ref:$r"; fi
  rm -rf "$tmp/bad"
done

echo "bootstrap tests: $passes passed, $fails failed"
[ "$fails" -eq 0 ]
