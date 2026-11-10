#!/usr/bin/env bash
# Stop hook: exit 2 blocks stopping; exit 0 means nothing is left behind.
#
# Vizra's rule (AGENTS.md "Git hygiene"): finished means merged, OR open with a
# pushed PR. This hook never asks an agent to merge: a pushed branch with an
# open PR passes. It audits the meta repo, the three nested component repos and
# every worktree of each, on every Stop (no session baseline).
#
# MAX_BLOCKS bounds the reminder counter, NEVER the checks. Repeating Stop must
# not turn unpushed work into apparent success.
# Must run on macOS bash 3.2: no ${var^^}, no associative arrays.
set -uo pipefail
MAX_BLOCKS=6
RECORDS_PREFIX="chore/warroom-records-"

payload="$(cat)"
start="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
if ! git -C "$start" rev-parse --git-dir >/dev/null 2>&1; then
  echo 'Cannot verify finished-means-merged: project root is not a git checkout.' >&2
  exit 2
fi
# A session may start inside a worktree; the nested repos live in the main checkout.
root="$(git -C "$start" worktree list --porcelain 2>/dev/null | sed -n '1s/^worktree //p')"
[ -n "$root" ] && [ -d "$root" ] || root="$start"

unfinished=""
add() { unfinished+="  - $1"$'\n'; }

# Hash the untrusted session id before using it as a filename.
session_key="$(python3 -c 'import hashlib,json,sys
try: value = str(json.load(sys.stdin).get("session_id", "unknown"))
except (ValueError, AttributeError): value = "unknown"
print(hashlib.sha256(value.encode()).hexdigest())' <<<"$payload")" || exit 2
state_dir="$root/.claude/hooks/.state"
state_file="$state_dir/$session_key"
blocks=0
if mkdir -p "$state_dir" 2>/dev/null; then
  [ -f "$state_file" ] && blocks="$(cat "$state_file" 2>/dev/null)"
  case "$blocks" in ''|*[!0-9]*) blocks=0 ;; esac
else
  add "cannot persist Stop reminder counter"
fi

pushed_check() { # repo name branch
  if git -C "$1" rev-parse --verify --quiet "$3@{u}" >/dev/null 2>&1; then
    ahead="$(git -C "$1" rev-list --count "$3@{u}..$3" 2>/dev/null)" || ahead=unknown
    [ "$ahead" = 0 ] || add "$2: branch '$3' has $ahead commit(s) not pushed to its upstream"
  else
    add "$2: branch '$3' has no upstream; push it"
  fi
}

check_repo() {
  repo="$1"
  name="$(basename "$repo")"

  # Worktrees have a .git FILE, not a directory; git itself lists them.
  wt_map=""
  wt_path=""
  while IFS= read -r line; do
    case "$line" in
      "worktree "*) wt_path="${line#worktree }"
        if [ -d "$wt_path" ]; then
          if ! git -C "$wt_path" diff --quiet --ignore-submodules 2>/dev/null ||
             ! git -C "$wt_path" diff --cached --quiet --ignore-submodules 2>/dev/null; then
            add "$name: uncommitted changes to tracked files in $wt_path"
          fi
        fi ;;
      "branch refs/heads/"*) wt_map+="${line#branch refs/heads/}"$'\t'"$wt_path"$'\n' ;;
    esac
  done <<EOT
$(git -C "$repo" worktree list --porcelain 2>/dev/null)
EOT

  # Refresh the remote first: a stale origin must not certify pushed or merged.
  if ! git -C "$repo" fetch --quiet --prune origin 2>/dev/null; then
    add "$name: cannot fetch origin; pushed and merged state is unverified"
    return
  fi
  if ! prs="$(cd "$repo" && gh pr list --state all --limit 1000 \
      --json number,state,headRefName,headRefOid,isCrossRepository 2>/dev/null)"; then
    add "$name: gh could not list pull requests; PR state is unverified"
    return
  fi
  # One line per head branch: OPEN beats MERGED beats CLOSED, newest PR wins.
  if ! pr_table="$(printf '%s' "$prs" | python3 -c 'import json,sys
rank = {"OPEN": 3, "MERGED": 2, "CLOSED": 1}
best = {}
for pr in json.load(sys.stdin):
    if pr.get("isCrossRepository"):
        continue
    key = (rank.get(pr["state"], 0), pr["number"])
    head = pr["headRefName"]
    if head not in best or key > best[head][0]:
        best[head] = (key, pr)
for head, (_, pr) in sorted(best.items()):
    print("\t".join([head, pr["state"], str(pr["number"]), pr["headRefOid"]]))')"; then
    add "$name: gh returned an unreadable pull request list; PR state is unverified"
    return
  fi

  while IFS= read -r branch; do
    [ -n "$branch" ] || continue
    case "$branch" in
      main) pushed_check "$repo" "$name" "$branch"; continue ;;
      "$RECORDS_PREFIX"*) pushed_check "$repo" "$name" "$branch"; continue ;;
    esac
    row="$(printf '%s\n' "$pr_table" | awk -F '\t' -v b="$branch" '$1 == b { print $2 "\t" $3 "\t" $4 }')"
    state="$(printf '%s' "$row" | cut -f1)"
    number="$(printf '%s' "$row" | cut -f2)"
    oid="$(printf '%s' "$row" | cut -f3)"
    where="$(printf '%s' "$wt_map" | awk -F '\t' -v b="$branch" '$1 == b { print $2 }')"
    [ -n "$where" ] && where=" (checked out at $where)"
    case "$state" in
      OPEN)
        pushed_check "$repo" "$name" "$branch" ;;
      MERGED)
        if [ "$(git -C "$repo" rev-parse "refs/heads/$branch" 2>/dev/null)" = "$oid" ]; then
          add "$name: PR #$number is merged but branch '$branch' still exists$where; remove the worktree and delete the branch"
        else
          add "$name: branch '$branch'$where has commits that are not in merged PR #$number and no open PR; push them and open a PR (do not delete)"
        fi ;;
      CLOSED)
        add "$name: PR #$number for branch '$branch'$where was closed unmerged and no PR is open; open a PR, or confirm it is pushed and delete only the LOCAL branch"
        pushed_check "$repo" "$name" "$branch" ;;
      *)
        add "$name: branch '$branch'$where has no open or merged PR; push it and open one"
        pushed_check "$repo" "$name" "$branch" ;;
    esac
  done <<EOT
$(git -C "$repo" for-each-ref --format='%(refname:short)' refs/heads 2>/dev/null)
EOT
}

check_repo "$root"
for component in core user search; do
  variable="VIZRA_$(printf %s "$component" | tr "[:lower:]" "[:upper:]")_ROOT"
  repo="${!variable:-$root/vizra-$component}"
  # A component that is not checked out has nothing local to lose.
  [ -e "$repo/.git" ] && check_repo "$repo"
done

if [ -z "$unfinished" ]; then
  rm -f "$state_file" 2>/dev/null
  exit 0
fi
if [ "$blocks" -lt "$MAX_BLOCKS" ]; then
  blocks=$((blocks + 1))
fi
printf '%s\n' "$blocks" > "$state_file" 2>/dev/null || true
# On exit 2 Claude Code relays STDERR only (vidra, 2026-10-12): the reason goes there.
cat >&2 <<EOT
AGENTS.md "Git hygiene" is not satisfied:

$unfinished
Commit and push your own work and open a PR; an open, pushed PR is enough.
Delete branches and worktrees whose PR is merged. Never delete unmerged work,
never merge a PR to satisfy this hook (AGENTS.md "Merge authorization" decides
merges), and do not commit changes that predate this task or belong to someone
else: report them. This hook stays blocking; reminder $blocks/$MAX_BLOCKS is
not permission to declare done.
EOT
exit 2
