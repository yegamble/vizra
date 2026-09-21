#!/usr/bin/env bash
#
# The fan-in guard for the vizra META repo (ADR-002 § CI fan-in and merge queue).
#
# It is a script rather than an inline workflow step so it can be run and
# demonstrated outside GitHub Actions. CODEOWNERS puts it under owner review.
#
# It enforces, about .github/required-checks.txt — which the PR under test is
# able to edit — and about the workflows themselves:
#
#   1. a FLOOR of lanes that may never be removed from the manifest;
#   2. every entry is a bare job name, so a lane cannot be neutered in place;
#   3. every entry names a job that actually exists;
#   4. no `continue-on-error` anywhere in the workflows, by PARSING them;
#   5. every action reference is pinned to a 40-hex commit SHA, and every
#      required lane is triggered on `pull_request` for ANY base branch;
#   6. the negative fixtures still trip the checker, each for its own rule.

set -euo pipefail

manifest=".github/required-checks.txt"
test -s "$manifest" || { echo "$manifest is missing or empty"; exit 1; }
# `|| true` is load-bearing. grep exits 1 when nothing matches, and under
# `set -e` the assignment then kills this script on the spot — so a manifest
# emptied down to its comments exited 1 with NO MESSAGE AT ALL, which is a
# terrible error for the one gate that decides whether a PR may merge. The
# explicit test below is what must report it.
required="$(grep -vE '^\s*(#|$)' "$manifest" | tr -d '\r' || true)"
test -n "$required" || {
  echo "EMPTY MANIFEST: $manifest lists no checks."
  echo '  Every line is blank or a comment, so ci-required would require nothing and'
  echo '  pass trivially. A manifest that gates nothing is not a manifest.'
  exit 1
}
echo "required checks:"; echo "$required" | sed 's/^/  - /'

# ADR-002: the fan-in guard rejects `continue-on-error` on any required lane,
# because a lane that cannot fail is not a gate.
#
# This PARSES the workflows rather than grepping them. A literal grep is evaded
# by a quoted key, a capitalised key, or a value that is a ${{ }} expression,
# and it also trips over its own error message. scripts/check-workflows.py
# matches the key after unquoting and case-folding, ignores the value entirely
# (`false` is refused too: "currently false" is not a property CI can rely on),
# and fails closed on a workflow it cannot parse.
if ! ./scripts/check-workflows.py; then
  echo "continue-on-error is not allowed on a required lane"
  exit 1
fi

# Action pins and trigger coverage, also by parse. An unpinned action is a
# mutable dependency; an untriggered required lane is a check that never runs,
# which ci-required-select.sh correctly refuses to call a pass — but a 30-minute
# timeout is a worse error message than an immediate one.
if ! ./scripts/check-action-pins.py --required "$manifest"; then
  echo "an action is unpinned, or a required lane is not triggered on pull_request"
  exit 1
fi

# FLOOR. The manifest is read from the checkout under test, so the PR being
# gated can edit it. Checking only that every name PRESENT maps to a real job is
# not enough: deleting a lane's line would leave this check green with that lane
# no longer required.
#
# The floor lives HERE, in scripts/ci-required-guard.sh — not in the workflow
# and not in the manifest it guards. Being one file away from the manifest is a
# speed bump, not a control: this script is also checked out from the PR under
# test and could be edited in the same commit. What actually closes it is the
# owner ruleset requiring CODEOWNERS review on /.github/ and /scripts/, which is
# an owner action after this PR lands (ADR-002 item 9: "application happens
# after PR1 lands, because ci-required must exist before it can be required")
# and is NOT part of it. GitHub rulesets additionally return 403 on this
# repository's current plan. Until that ruleset is applied, "ci-required is the
# gate" is a convention, and this comment says so rather than implying otherwise.
floor="validate"
absent=0
while IFS= read -r lane; do
  lane="$(printf '%s' "$lane" | tr -d '[:space:]')"
  [ -z "$lane" ] && continue
  if ! printf '%s\n' "$required" | grep -qxF "$lane"; then
    echo "FLOOR VIOLATION: '$lane' is a non-optional lane and must appear in $manifest, but it is absent."
    echo "  A PR may add lanes to the manifest. It may not remove one of the floor lanes,"
    echo "  because that would silently stop gating the thing the lane exists to gate."
    absent=1
  fi
done <<< "$floor"
test "$absent" = "0" || exit 1
echo "floor: every non-optional lane is present in the manifest"

# A manifest entry must be a bare job name. Any annotation — a trailing comment,
# an "optional" marker, a colon-separated field — is refused, so a lane cannot
# be neutered in place instead of being deleted.
if printf '%s\n' "$required" | grep -nvE '^[a-z0-9][a-z0-9-]*$'; then
  echo "a required-check entry must be a bare lowercase job name with no annotation"
  exit 1
fi
echo "manifest entries are bare job names"

# Every required check must exist as a job in a workflow — or the aggregate
# would wait forever for something nobody defined — and every step of that job
# must actually run.
#
# This was a grep:
#     grep -qE "^  ${check}:[[:space:]]*$" .github/workflows/*.yml
# which is indentation-sensitive and matches only *.yml, while every other
# checker here globs *.yml AND *.yaml. A required lane defined in a .yaml
# workflow was reported as having no job at all. It is now a parse, like the
# rest, and the same checker refuses the two ways to neuter a lane that
# `continue-on-error` does not cover: a `defaults.run.shell` override (the
# Actions analogue of `SHELL := /usr/bin/true`) and a step-level `if:`.
if ! ./scripts/check-lane-integrity.py --required "$manifest"; then
  echo "a required lane is undefined, shell-overridden, or has a conditional step"
  exit 1
fi

# The workflow checker must itself still reject every spelling it exists to
# catch. A checker that silently stopped matching would leave the gate open, so
# its fixtures are exercised on every run rather than only in a demonstration.
#
# The fixture set is a FLOOR, checked by name, exactly like the lane floor above
# and for the same reason. `for fixture in scripts/testdata/*.yml` alone is
# green when the fixtures are gone: with no match bash passes the literal glob
# through, the checker is handed a path that does not exist and exits non-zero,
# and the "must be rejected" branch reads that as a pass.
#
# A fixture must also be rejected FOR THE REASON IT WAS WRITTEN TO TRIP. Reading
# any non-zero exit as "correctly rejected" leaves the same hole one level down:
# a checker that cannot read, or cannot parse, its input also exits non-zero, so
# an EMPTIED fixture — the case that reaches CI through git — would keep this
# guard at exit 0 while printing a fixture count it had not earned.
#
# check-workflows.py therefore answers three ways — 0 clean, 1 VIOLATION,
# 2 UNEVALUABLE — and each reject fixture below DECLARES the rule it must trip.
# The guard requires exit 1 exactly, and requires the reported rule to be the
# declared one. Exit 2 is a named guard failure, never a pass.
fixtures_dir="scripts/testdata"
accept_fixture="wf-clean.yml"
#            fixture|at|key spelling|value kind
reject_fixtures="wf-plain.yml|job|continue-on-error|literal-true
wf-quoted-key.yml|job|\"continue-on-error\"|literal-true
wf-capitalised.yml|job|Continue-On-Error|literal-true
wf-expression.yml|step|continue-on-error|expression
wf-false.yml|step|continue-on-error|literal-false"

# The declared set is itself a floor. Without this, deleting a row above would
# lower the fixture floor from 6 to 5 and the guard would still print a tidy
# "N fixtures exercised, floor N" — a count that moved to match whatever was
# left, which is the same class of false green this script exists to remove.
expected_reject_fixtures=5
declared_reject_fixtures="$(printf '%s\n' "$reject_fixtures" | grep -c .)"
if [ "$declared_reject_fixtures" != "$expected_reject_fixtures" ]; then
  echo "FIXTURE FLOOR CHANGED: $declared_reject_fixtures reject-fixture rule(s) are declared;"
  echo "  expected_reject_fixtures says $expected_reject_fixtures."
  echo "  A spelling of continue-on-error was added or removed. If that was deliberate, change"
  echo "  expected_reject_fixtures in the same commit so the floor is a decision, not a"
  echo "  consequence of whatever rows happen to be left."
  exit 1
fi

test -d "$fixtures_dir" || {
  echo "MISSING FIXTURES: '$fixtures_dir' does not exist."
  echo "  The workflow checker's negative fixtures are what prove it still catches every"
  echo "  spelling of continue-on-error. With the directory gone there is nothing to prove"
  echo "  it with, and this guard must not pass by default."
  exit 1
}

missing_fixture=0
for entry in "$accept_fixture" $(printf '%s\n' "$reject_fixtures" | cut -d'|' -f1); do
  if [ ! -f "$fixtures_dir/$entry" ]; then
    echo "MISSING FIXTURE: '$fixtures_dir/$entry' is a non-optional fixture and is absent."
    echo "  It is in the floor because the checker must keep proving it handles that spelling."
    missing_fixture=1
  fi
done
test "$missing_fixture" = "0" || exit 1

# Readable and non-empty, checked separately and BEFORE the checker runs, so an
# unusable fixture is never mistaken for a rejected one.
unusable=0
for entry in "$accept_fixture" $(printf '%s\n' "$reject_fixtures" | cut -d'|' -f1); do
  f="$fixtures_dir/$entry"
  if [ ! -r "$f" ]; then
    echo "UNUSABLE FIXTURE: '$f' exists but is not readable."
    unusable=1
  elif [ ! -s "$f" ]; then
    echo "UNUSABLE FIXTURE: '$f' is empty."
    echo "  An empty fixture tests nothing; the checker reports UNEVALUABLE, not a rejection."
    unusable=1
  fi
done
test "$unusable" = "0" || exit 1

# Now run every fixture actually present — the floor above is a minimum, not a
# maximum, so a fixture added later is exercised too. An empty glob is refused
# rather than skipped.
shopt -s nullglob
present=("$fixtures_dir"/wf-*.yml)
shopt -u nullglob
if [ "${#present[@]}" -eq 0 ]; then
  echo "NO FIXTURES MATCHED: '$fixtures_dir/wf-*.yml' matched nothing."
  echo "  An empty fixture glob must fail loudly; it previously left this guard green."
  exit 1
fi

declared_rule() {
  printf '%s\n' "$reject_fixtures" | awk -F'|' -v want="$1" \
    '$1 == want { print $2 "|" $3 "|" $4 }'
}

checked=0
for fixture in "${present[@]}"; do
  base="$(basename "$fixture")"
  if [ ! -r "$fixture" ] || [ ! -s "$fixture" ]; then
    echo "UNUSABLE FIXTURE: '$fixture' is unreadable or empty; it cannot be exercised."
    exit 1
  fi
  set +e
  out="$(./scripts/check-workflows.py "$fixture" 2>&1)"
  rc=$?
  set -e
  case "$fixture" in
    *"/$accept_fixture")
      if [ "$rc" != "0" ]; then
        echo "the workflow checker did not accept its own clean fixture: $fixture (exit $rc)"
        printf '%s\n' "$out" | sed 's/^/    /'
        exit 1
      fi
      ;;
    *)
      # Exit 1 EXACTLY. 0 means it accepted a file it must catch; 2 means it
      # could not evaluate the file at all, which is not a rejection.
      if [ "$rc" = "0" ]; then
        echo "the workflow checker ACCEPTED $fixture, which spells continue-on-error in a way it must catch"
        exit 1
      fi
      if [ "$rc" != "1" ]; then
        echo "UNEVALUABLE FIXTURE: the workflow checker could not evaluate $fixture (exit $rc)."
        echo "  Nothing was checked. This is a guard failure, not a rejection."
        printf '%s\n' "$out" | sed 's/^/    /'
        exit 1
      fi
      rule="$(declared_rule "$base")"
      if [ -n "$rule" ]; then
        want_at="$(printf '%s' "$rule" | cut -d'|' -f1)"
        want_key="$(printf '%s' "$rule" | cut -d'|' -f2)"
        want_value="$(printf '%s' "$rule" | cut -d'|' -f3)"
        want_line="VIOLATION $fixture at=$want_at key=$want_key value=$want_value"
        if ! printf '%s\n' "$out" | grep -qF "$want_line"; then
          echo "WRONG RULE TRIPPED: $fixture was rejected, but not for the rule it declares."
          echo "  declared: $want_line"
          echo "  reported:"
          printf '%s\n' "$out" | grep '^VIOLATION ' | sed 's/^/    /' || echo "    (no VIOLATION line at all)"
          exit 1
        fi
      fi
      ;;
  esac
  checked=$((checked + 1))
done

floor_count=$((expected_reject_fixtures + 1))
if [ "$checked" -lt "$floor_count" ]; then
  echo "only $checked fixture(s) were exercised; the floor is $floor_count"
  exit 1
fi
echo "the workflow checker rejects every continue-on-error spelling in $fixtures_dir/ ($checked fixtures exercised, floor $floor_count)"

# The SAME treatment for scripts/check-action-pins.py. A rule with no negative
# fixture is a rule nobody has seen fail, and an unpinned action or an
# untriggered lane is precisely the kind of thing a checker can silently stop
# catching after a refactor.
#
# `pin-*.yml`, not `wf-*.yml`, so the two fixture sets cannot be confused: the
# loop above would otherwise read a pin fixture as a continue-on-error reject
# fixture and demand a VIOLATION line it never emits.
#
#              fixture|reason reported by check-action-pins.py
pin_accept_fixture="pin-clean.yml"
pin_reject_fixtures="pin-tag.yml|not-a-40-hex-sha
pin-short-sha.yml|not-a-40-hex-sha
pin-no-ref.yml|no-ref
pin-docker.yml|docker-image
pin-base-filter.yml|base-branch-filter
pin-no-pull-request.yml|not-triggered-on-pull-request"

expected_pin_fixtures=6
declared_pin_fixtures="$(printf '%s\n' "$pin_reject_fixtures" | grep -c .)"
if [ "$declared_pin_fixtures" != "$expected_pin_fixtures" ]; then
  echo "PIN FIXTURE FLOOR CHANGED: $declared_pin_fixtures rule(s) are declared;"
  echo "  expected_pin_fixtures says $expected_pin_fixtures."
  echo "  A pin/trigger rule was added or retired. If that was deliberate, change"
  echo "  expected_pin_fixtures in the same commit so the floor is a decision."
  exit 1
fi

for entry in "$pin_accept_fixture" $(printf '%s\n' "$pin_reject_fixtures" | cut -d'|' -f1); do
  f="$fixtures_dir/$entry"
  if [ ! -f "$f" ]; then
    echo "MISSING FIXTURE: '$f' is a non-optional pin/trigger fixture and is absent."
    exit 1
  fi
  if [ ! -r "$f" ] || [ ! -s "$f" ]; then
    echo "UNUSABLE FIXTURE: '$f' is unreadable or empty; an unusable fixture is not a rejection."
    exit 1
  fi
done

shopt -s nullglob
pin_present=("$fixtures_dir"/pin-*.yml)
shopt -u nullglob
if [ "${#pin_present[@]}" -eq 0 ]; then
  echo "NO PIN FIXTURES MATCHED: '$fixtures_dir/pin-*.yml' matched nothing."
  exit 1
fi

pin_declared_reason() {
  printf '%s\n' "$pin_reject_fixtures" | awk -F'|' -v want="$1" '$1 == want { print $2 }'
}

pin_checked=0
for fixture in "${pin_present[@]}"; do
  base="$(basename "$fixture")"
  set +e
  out="$(./scripts/check-action-pins.py --required "$manifest" "$fixture" 2>&1)"
  rc=$?
  set -e
  if [ "$base" = "$pin_accept_fixture" ]; then
    if [ "$rc" != "0" ]; then
      echo "the pin checker did not accept its own clean fixture: $fixture (exit $rc)"
      printf '%s\n' "$out" | sed 's/^/    /'
      exit 1
    fi
  else
    # Exit 1 EXACTLY, for the same reason as above: exit 2 is UNEVALUABLE, and
    # a file the checker could not read was never rejected.
    if [ "$rc" = "0" ]; then
      echo "the pin checker ACCEPTED $fixture, which it must catch"
      exit 1
    fi
    if [ "$rc" != "1" ]; then
      echo "UNEVALUABLE FIXTURE: the pin checker could not evaluate $fixture (exit $rc)."
      echo "  Nothing was checked. This is a guard failure, not a rejection."
      printf '%s\n' "$out" | sed 's/^/    /'
      exit 1
    fi
    want_reason="$(pin_declared_reason "$base")"
    if [ -n "$want_reason" ] && ! printf '%s\n' "$out" | grep -qF "reason=$want_reason"; then
      echo "WRONG RULE TRIPPED: $fixture was rejected, but not for the rule it declares."
      echo "  declared: reason=$want_reason"
      echo "  reported:"
      printf '%s\n' "$out" | grep -o 'reason=[a-z0-9-]*' | sed 's/^/    /' || echo "    (no reason= at all)"
      exit 1
    fi
  fi
  pin_checked=$((pin_checked + 1))
done

pin_floor=$((expected_pin_fixtures + 1))
if [ "$pin_checked" -lt "$pin_floor" ]; then
  echo "only $pin_checked pin fixture(s) were exercised; the floor is $pin_floor"
  exit 1
fi
echo "the pin checker rejects every unpinned-action and untriggered-lane spelling in $fixtures_dir/ ($pin_checked fixtures exercised, floor $pin_floor)"

# And the same again for scripts/check-lane-integrity.py.
#
# `lane-*.yml` plus ONE `.yaml` accept fixture — the extension is the point of
# that one: job existence used to be a grep over *.yml only, so a required lane
# defined in a .yaml workflow was reported as missing. The fixture fails if that
# regresses.
lane_accept_fixtures="lane-clean.yml
lane-yaml-extension.yaml"
#               fixture|reason reported by check-lane-integrity.py
lane_reject_fixtures="lane-workflow-shell.yml|defaults-shell-override
lane-job-shell.yml|defaults-shell-override
lane-if-false.yml|constant-false-if
lane-if-expression.yml|conditional-step-on-required-lane
lane-missing-job.yml|no-such-job"

expected_lane_fixtures=5
declared_lane_fixtures="$(printf '%s\n' "$lane_reject_fixtures" | grep -c .)"
if [ "$declared_lane_fixtures" != "$expected_lane_fixtures" ]; then
  echo "LANE FIXTURE FLOOR CHANGED: $declared_lane_fixtures rule(s) are declared;"
  echo "  expected_lane_fixtures says $expected_lane_fixtures."
  exit 1
fi

for entry in $(printf '%s\n' "$lane_accept_fixtures") $(printf '%s\n' "$lane_reject_fixtures" | cut -d'|' -f1); do
  f="$fixtures_dir/$entry"
  if [ ! -f "$f" ]; then
    echo "MISSING FIXTURE: '$f' is a non-optional lane-integrity fixture and is absent."
    exit 1
  fi
  if [ ! -r "$f" ] || [ ! -s "$f" ]; then
    echo "UNUSABLE FIXTURE: '$f' is unreadable or empty; an unusable fixture is not a rejection."
    exit 1
  fi
done

shopt -s nullglob
lane_present=("$fixtures_dir"/lane-*.yml "$fixtures_dir"/lane-*.yaml)
shopt -u nullglob
if [ "${#lane_present[@]}" -eq 0 ]; then
  echo "NO LANE FIXTURES MATCHED: '$fixtures_dir/lane-*' matched nothing."
  exit 1
fi

lane_declared_reason() {
  printf '%s\n' "$lane_reject_fixtures" | awk -F'|' -v want="$1" '$1 == want { print $2 }'
}

lane_checked=0
for fixture in "${lane_present[@]}"; do
  base="$(basename "$fixture")"
  set +e
  out="$(./scripts/check-lane-integrity.py --required "$manifest" "$fixture" 2>&1)"
  rc=$?
  set -e
  if printf '%s\n' "$lane_accept_fixtures" | grep -qxF "$base"; then
    if [ "$rc" != "0" ]; then
      echo "the lane checker did not accept its own clean fixture: $fixture (exit $rc)"
      printf '%s\n' "$out" | sed 's/^/    /'
      exit 1
    fi
  else
    if [ "$rc" = "0" ]; then
      echo "the lane checker ACCEPTED $fixture, which it must catch"
      exit 1
    fi
    if [ "$rc" != "1" ]; then
      echo "UNEVALUABLE FIXTURE: the lane checker could not evaluate $fixture (exit $rc)."
      printf '%s\n' "$out" | sed 's/^/    /'
      exit 1
    fi
    want_reason="$(lane_declared_reason "$base")"
    if [ -n "$want_reason" ] && ! printf '%s\n' "$out" | grep -qF "reason=$want_reason"; then
      echo "WRONG RULE TRIPPED: $fixture was rejected, but not for the rule it declares."
      echo "  declared: reason=$want_reason"
      printf '%s\n' "$out" | grep -o 'reason=[a-z-]*' | sed 's/^/    /' || echo "    (no reason= at all)"
      exit 1
    fi
  fi
  lane_checked=$((lane_checked + 1))
done

lane_floor=$((expected_lane_fixtures + 2))
if [ "$lane_checked" -lt "$lane_floor" ]; then
  echo "only $lane_checked lane fixture(s) were exercised; the floor is $lane_floor"
  exit 1
fi
echo "the lane checker rejects every shell-override, conditional-step and missing-job case in $fixtures_dir/ ($lane_checked fixtures exercised, floor $lane_floor)"
