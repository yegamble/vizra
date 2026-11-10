#!/usr/bin/env bash
# Red and green cases for .claude/hooks/finished-means-merged.sh.
# Builds throwaway repos with local bare remotes and a stub `gh`; no network.
#   bash tests/warroom/stop_hook_test.sh [-v]
set -uo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
hook="$here/../../.claude/hooks/finished-means-merged.sh"
verbose="${1:-}"
work="$(mktemp -d "${TMPDIR:-/tmp}/vz-stop-hook-XXXXXX")"
trap 'rm -rf "$work"' EXIT

export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@example.invalid
export GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@example.invalid
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null

# Stub gh: prints $GH_STUB_DIR/<repo dir name>.json, or fails if FAIL exists.
mkdir -p "$work/bin"
cat > "$work/bin/gh" <<'STUB'
#!/usr/bin/env bash
[ "$1 $2" = "pr list" ] || { echo "stub gh: unexpected $*" >&2; exit 64; }
[ -e "$GH_STUB_DIR/FAIL" ] && exit 1
file="$GH_STUB_DIR/$(basename "$PWD").json"
if [ -f "$file" ]; then cat "$file"; else echo '[]'; fi
STUB
chmod +x "$work/bin/gh"
export PATH="$work/bin:$PATH"

pass=0
fail=0
T=""

fresh() {
  T="$(mktemp -d "$work/case-XXXXXX")"
  export GH_STUB_DIR="$T/gh"
  mkdir -p "$GH_STUB_DIR" "$T/remotes"
  for r in vizra vizra-core vizra-user vizra-search; do
    git init -q --bare -b main "$T/remotes/$r.git"
    if [ "$r" = vizra ]; then dest="$T/vizra"; else dest="$T/vizra/vizra-$(printf %s "$r" | cut -d- -f2)"; fi
    git clone -q "$T/remotes/$r.git" "$dest" 2>/dev/null
    git -C "$dest" checkout -q -b main 2>/dev/null
    echo "$r" > "$dest/README.md"
    git -C "$dest" add README.md
    git -C "$dest" commit -q -m init
    git -C "$dest" push -q -u origin main
  done
  export CLAUDE_PROJECT_DIR="$T/vizra"
}

pr() { # repo-dir-name state number branch oid
  printf '[{"number":%s,"state":"%s","headRefName":"%s","headRefOid":"%s","isCrossRepository":false}]\n' \
    "$3" "$2" "$4" "$5" > "$GH_STUB_DIR/$1.json"
}

branch_commit() { # repo branch
  git -C "$1" checkout -q -b "$2"
  echo change >> "$1/README.md"
  git -C "$1" commit -q -am "work on $2"
}

expect() { # label want-exit want-stderr-substring
  out="$T/out"
  err="$T/err"
  echo '{"session_id":"s1"}' | /bin/bash "$hook" >"$out" 2>"$err"
  got=$?
  ok=true
  [ "$got" = "$2" ] || ok=false
  if [ -n "$3" ] && ! grep -qF -- "$3" "$err"; then ok=false; fi
  if [ "$2" = 0 ] && [ -s "$err" ]; then ok=false; fi
  if $ok; then
    pass=$((pass + 1))
    echo "ok   $1 (exit $got)"
    [ "$verbose" = -v ] && sed 's/^/     | /' "$err"
  else
    fail=$((fail + 1))
    echo "FAIL $1: exit $got, wanted $2 with stderr containing '$3'"
    sed 's/^/     | /' "$err"
  fi
}

# ---- green
fresh
expect "green: clean main in all four repos" 0 ""

fresh
branch_commit "$T/vizra/vizra-core" feat/x
git -C "$T/vizra/vizra-core" push -q -u origin feat/x
pr vizra-core OPEN 7 feat/x "$(git -C "$T/vizra/vizra-core" rev-parse HEAD)"
expect "green: pushed branch with an open PR (never asked to merge)" 0 ""

fresh
git -C "$T/vizra" worktree add -q -b feat/wt "$T/wt" main 2>/dev/null
echo w >> "$T/wt/README.md"
git -C "$T/wt" commit -q -am wt
git -C "$T/wt" push -q -u origin feat/wt
pr vizra OPEN 3 feat/wt "$(git -C "$T/wt" rev-parse HEAD)"
expect "green: pushed worktree branch with an open PR" 0 ""
CLAUDE_PROJECT_DIR="$T/wt" expect "green: same, session started inside the worktree" 0 ""

fresh
branch_commit "$T/vizra" chore/warroom-records-2026-11-10
git -C "$T/vizra" push -q -u origin chore/warroom-records-2026-11-10
expect "green: pushed records branch with no PR" 0 ""

# ---- red
fresh
echo dirty >> "$T/vizra/vizra-user/README.md"
expect "red: dirty tracked file" 2 "vizra-user: uncommitted changes to tracked files"

fresh
echo more >> "$T/vizra/README.md"
git -C "$T/vizra" commit -q -am local
expect "red: unpushed commit on main" 2 "vizra: branch 'main' has 1 commit(s) not pushed"

fresh
branch_commit "$T/vizra/vizra-core" feat/x
git -C "$T/vizra/vizra-core" push -q -u origin feat/x
pr vizra-core OPEN 7 feat/x "$(git -C "$T/vizra/vizra-core" rev-parse HEAD)"
echo more >> "$T/vizra/vizra-core/README.md"
git -C "$T/vizra/vizra-core" commit -q -am more
expect "red: unpushed commit on an open-PR branch" 2 "vizra-core: branch 'feat/x' has 1 commit(s) not pushed"

fresh
branch_commit "$T/vizra/vizra-search" feat/nopush
pr vizra-search OPEN 2 feat/nopush "$(git -C "$T/vizra/vizra-search" rev-parse HEAD)"
expect "red: branch with no upstream" 2 "vizra-search: branch 'feat/nopush' has no upstream"

fresh
branch_commit "$T/vizra/vizra-core" feat/nopr
git -C "$T/vizra/vizra-core" push -q -u origin feat/nopr
expect "red: pushed branch with no PR" 2 "has no open or merged PR; push it and open one"

fresh
branch_commit "$T/vizra/vizra-user" feat/done
git -C "$T/vizra/vizra-user" push -q -u origin feat/done
pr vizra-user MERGED 9 feat/done "$(git -C "$T/vizra/vizra-user" rev-parse HEAD)"
git -C "$T/vizra/vizra-user" checkout -q main
expect "red: merged branch not deleted" 2 "vizra-user: PR #9 is merged but branch 'feat/done' still exists"
i=0
while [ "$i" -lt 8 ]; do echo '{"session_id":"s1"}' | /bin/bash "$hook" >/dev/null 2>&1; i=$((i + 1)); done
expect "red: still blocking after 9 Stops (the reminder cap is not a bypass)" 2 "reminder 6/6 is"

fresh
git -C "$T/vizra" worktree add -q -b feat/wtdone "$T/wt" main 2>/dev/null
git -C "$T/wt" push -q -u origin feat/wtdone
pr vizra MERGED 4 feat/wtdone "$(git -C "$T/wt" rev-parse HEAD)"
expect "red: merged worktree not removed" 2 "is merged but branch 'feat/wtdone' still exists (checked out at $(cd "$T/wt" && pwd -P))"

fresh
branch_commit "$T/vizra/vizra-core" feat/reused
git -C "$T/vizra/vizra-core" push -q -u origin feat/reused
pr vizra-core MERGED 5 feat/reused 0000000000000000000000000000000000000000
expect "red: commits after a merged PR are not called deletable" 2 "push them and open a PR (do not delete)"

fresh
branch_commit "$T/vizra/vizra-core" feat/closed
git -C "$T/vizra/vizra-core" push -q -u origin feat/closed
pr vizra-core CLOSED 6 feat/closed "$(git -C "$T/vizra/vizra-core" rev-parse HEAD)"
expect "red: closed-unmerged PR with no open PR" 2 "was closed unmerged"

fresh
touch "$GH_STUB_DIR/FAIL"
expect "red: gh failure is unverified, not a pass" 2 "PR state is unverified"

fresh
rm -rf "$T/remotes/vizra-search.git"
expect "red: fetch failure is unverified, not a pass" 2 "vizra-search: cannot fetch origin"

fresh
out="$T/out"
if echo 'not json' | /bin/bash "$hook" >"$out" 2>"$T/err" && [ ! -s "$out" ]; then pass=$((pass + 1)); echo "ok   green: malformed payload still audits"; else fail=$((fail + 1)); echo "FAIL malformed payload"; fi

echo "stop hook: $pass passed, $fail failed"
[ "$fail" = 0 ]
