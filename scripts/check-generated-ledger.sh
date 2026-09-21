#!/usr/bin/env bash
#
# The generated ledger must be reproducible from its sources.
#
# `docs/quality/features.json` is GENERATED from `docs/evidence/ledger-generator/`
# (AGENTS.md § Engineering guardrails: "regenerate ... never hand-edit generated
# files"). Two different mistakes produce the same wrong state and this check
# catches both, because it regenerates rather than inspecting:
#
#   1. someone hand-edited the JSON;
#   2. someone edited a generator source and did not regenerate.
#
# In both cases re-running the generator produces bytes that differ from the
# committed file, and `git diff --exit-code` goes red NAMING the file.
#
# It is a script rather than an inline workflow step so it can be run and
# demonstrated outside GitHub Actions. CODEOWNERS puts it under owner review.

set -euo pipefail

generator_dir="docs/evidence/ledger-generator"
entrypoint="$generator_dir/build.py"

# The files the generator writes, declared here rather than inferred.
#
# `build.py` writes exactly one file: its argv[1]. `docs/quality/ui-controls.json`
# and `docs/quality/release-profiles/*.json` are NOT generated — no generator
# source references them — so they are hand-authored siblings and are covered by
# scripts/check-quality-json.py instead, not by this regeneration check.
#
# If the generator is ever taught to write a second file, add it here. The
# "nothing else moved" assertion below turns that omission red rather than
# letting a new generated file go unguarded.
declare -a generated=(
  "docs/quality/features.json"
)

test -f "$entrypoint" || {
  echo "MISSING GENERATOR: $entrypoint does not exist."
  echo "  This check regenerates the ledger; with no generator there is nothing to"
  echo "  check against and it must not pass by default."
  exit 1
}

for f in "${generated[@]}"; do
  test -f "$f" || {
    echo "MISSING GENERATED FILE: $f is declared as generated but does not exist."
    exit 1
  }
done

# The working tree must be clean for the declared files BEFORE we regenerate,
# otherwise a pre-existing local edit would be blamed on the generator (or,
# worse, would mask a real difference).
if ! git diff --quiet -- "${generated[@]}"; then
  echo "DIRTY WORKING TREE: the generated file(s) already differ from HEAD before regeneration:"
  git diff --name-only -- "${generated[@]}" | sed 's/^/  - /'
  echo "  Commit or revert them first; this check cannot attribute a difference it did not cause."
  exit 1
fi

before="$(git status --porcelain -- docs/quality | sort)"

# DELETE the declared files before regenerating.
#
# Without this, `git diff --exit-code` alone cannot tell "the generator rewrote
# the file identically" from "the generator wrote NOTHING". A build.py gutted to
#
#     print("OK 191 requirements; core=141")
#
# exits 0, touches nothing, and every later assertion passes — the check then
# prints "generated ledger reproduces byte-for-byte" while nothing was
# regenerated at all. That is the exact false-positive-CI class AGENTS.md tells
# reviewers to hunt, and it made this lane's primary assertion vacuous.
#
# With the files removed first, a generator that writes nothing leaves a
# DELETION that `git diff --exit-code` sees, and the existence check below names
# it. The generator's real output set is then whatever reappears, which is what
# makes the set-equality assertion below meaningful rather than assumed.
rm -f "${generated[@]}"

echo "regenerating with: $(python3 --version 2>&1)"
# The generator is its own validator: unique ids, required fields, resolvable
# dependencies, no cycles, core-profile closure. A non-zero exit here is a
# broken ledger SOURCE, which is a different failure from a stale output.
( cd "$generator_dir" && python3 build.py ../../quality/features.json ) || {
  echo "GENERATOR FAILED: $entrypoint exited non-zero."
  echo "  The ledger sources do not validate. This is a source error, not a stale output."
  echo "  The declared generated file(s) were removed before this run; restore them with"
  echo "      git checkout -- ${generated[*]}"
  exit 1
}

# Each declared file must now EXIST, be NON-EMPTY, and PARSE. A generator that
# wrote nothing, wrote only some of its outputs, or wrote a truncated or empty
# file is caught here by name — before the diff, so the message says what is
# actually wrong instead of showing a deletion hunk.
rc=0
for f in "${generated[@]}"; do
  if [ ! -e "$f" ]; then
    echo "GENERATOR WROTE NOTHING: '$f' is declared as generated but does not exist after running the generator."
    echo "  It was removed before regeneration, so the generator did not write it."
    echo "  A generator that exits 0 without writing its output is not a reproduction."
    rc=1
    continue
  fi
  if [ ! -s "$f" ]; then
    echo "GENERATOR WROTE AN EMPTY FILE: '$f' exists but is zero bytes."
    rc=1
    continue
  fi
  if ! python3 -c 'import json,sys; json.load(open(sys.argv[1],encoding="utf-8"))' "$f" 2>/dev/null; then
    echo "GENERATOR WROTE INVALID JSON: '$f' does not parse."
    echo "  A truncated write — for example a locale that cannot encode the ledger's"
    echo "  non-ASCII characters — leaves exactly this state."
    rc=1
  fi
done
test "$rc" = "0" || {
  echo
  echo "Restore the removed file(s) with: git checkout -- ${generated[*]}"
  exit 1
}

if ! git diff --exit-code -- "${generated[@]}"; then
  rc=1
  echo
  echo "GENERATED FILE IS NOT REPRODUCIBLE. The following generated file(s) changed when"
  echo "the generator was re-run, which means the committed copy does not match its sources:"
  git diff --name-only -- "${generated[@]}" | sed 's/^/  - /'
  echo
  echo "  Either the file was hand-edited (AGENTS.md forbids it), or a generator source"
  echo "  under $generator_dir was changed without regenerating."
  echo "  Fix: edit the sources, run"
  echo "      (cd $generator_dir && python3 build.py ../../quality/features.json)"
  echo "  and commit BOTH the sources and the regenerated file."
fi

# SET EQUALITY, in the other direction: nothing the generator writes may be
# outside the declared list. A new generated file that nobody declared would
# otherwise never be diffed, so it could be hand-edited freely. Combined with
# the existence check above — which proves every DECLARED file was written —
# this makes the declared list and the generator's actual output set the same
# set, rather than one being assumed to cover the other.
after="$(git status --porcelain -- docs/quality | sort)"
if [ "$before" != "$after" ]; then
  undeclared="$(comm -13 <(printf '%s\n' "$before") <(printf '%s\n' "$after") | awk '{print $2}')"
  for f in $undeclared; do
    declared=0
    for g in "${generated[@]}"; do [ "$f" = "$g" ] && declared=1; done
    if [ "$declared" = "0" ]; then
      echo "UNDECLARED GENERATED FILE: the generator wrote '$f', which is not in the declared list."
      echo "  Add it to \`generated\` in $0 so it is diffed too."
      rc=1
    fi
  done
fi

test "$rc" = "0" || exit "$rc"

# LOCALE REGRESSION. The generator writes non-ASCII characters (§ ° × – — … ← →
# ↔ ≤ ≥). Before the explicit `encoding="utf-8"` was added, it opened its output
# with the ambient locale's encoding, and under a C/POSIX locale that is ASCII:
# the write raised UnicodeEncodeError partway through and left a TRUNCATED
# features.json behind.
#
# That is not a hypothetical. It reproduces on macOS and on Linux with exactly
# the environment below. PEP 538's C-locale coercion is what normally hides it,
# which is why PYTHONCOERCECLOCALE=0 and PYTHONUTF8=0 are both required to see
# it — and why "it works on my machine and on the runner" was never evidence
# that the generator was locale-independent.
#
# So the property is re-asserted here rather than trusted: regenerate once under
# that environment and require the output to be byte-identical again.
echo "locale regression: re-running under LC_ALL=C LANG=POSIX PYTHONCOERCECLOCALE=0 PYTHONUTF8=0"
rm -f "${generated[@]}"
if ! ( cd "$generator_dir" && env LC_ALL=C LANG=POSIX PYTHONCOERCECLOCALE=0 PYTHONUTF8=0 \
         python3 build.py ../../quality/features.json >/dev/null ); then
  echo "LOCALE REGRESSION: the generator failed under a C/POSIX locale."
  echo "  This is the pre-fix failure returning: an output opened without an explicit"
  echo "  encoding= is written in the ambient locale's encoding, which is ASCII here,"
  echo "  and the ledger's non-ASCII characters cannot be encoded."
  echo "  Restore the removed file(s) with: git checkout -- ${generated[*]}"
  exit 1
fi
for f in "${generated[@]}"; do
  if [ ! -s "$f" ]; then
    echo "LOCALE REGRESSION: '$f' is missing or empty after the C/POSIX-locale run."
    echo "  Restore it with: git checkout -- ${generated[*]}"
    exit 1
  fi
done
if ! git diff --exit-code -- "${generated[@]}"; then
  echo
  echo "LOCALE REGRESSION: the generator produced DIFFERENT bytes under a C/POSIX locale."
  echo "  The generated ledger must not depend on the locale of whoever regenerates it."
  exit 1
fi

echo "generated ledger reproduces byte-for-byte: ${generated[*]} (UTF-8 and C/POSIX locales)"
exit 0
