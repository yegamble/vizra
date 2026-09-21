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

echo "regenerating with: $(python3 --version 2>&1)"
# The generator is its own validator: unique ids, required fields, resolvable
# dependencies, no cycles, core-profile closure. A non-zero exit here is a
# broken ledger SOURCE, which is a different failure from a stale output.
( cd "$generator_dir" && python3 build.py ../../quality/features.json ) || {
  echo "GENERATOR FAILED: $entrypoint exited non-zero."
  echo "  The ledger sources do not validate. This is a source error, not a stale output."
  exit 1
}

rc=0
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

# Nothing the generator writes may be outside the declared list. A new generated
# file that nobody declared would otherwise slip past this check entirely.
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

if [ "$rc" = "0" ]; then
  echo "generated ledger reproduces byte-for-byte: ${generated[*]}"
fi
exit "$rc"
