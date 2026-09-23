#!/usr/bin/env bash
#
# Red/green demonstrations for "the ledger can record status, but only with
# evidence" (war-room queue 2i). Run from anywhere:
#
#     bash docs/evidence/ledger-status/demo.sh 2>&1 | tee demo-transcript.txt
#
# The `validate` lane runs this on every pull request, so a guard that silently
# stopped refusing something turns the lane red instead of staying green.
#
# EVERY RECORD AND EVIDENCE FILE THIS SCRIPT WRITES IS A FIXTURE, NOT A CLAIM.
# The committed status_records.json is restored byte-for-byte at the end, the
# fixture evidence file is deleted, and the script fails if `git status` differs
# from what it was at the start.
#
# How a case is scored, following docs/evidence/compose-topology/demo.sh:
#   - every mutation prints the sha256 of the file before and after, and the case
#     is REFUSED if they are equal (a mutation that did not apply cannot be
#     recorded as "the guard caught it");
#   - a red case must exit non-zero AND print the named reason; a non-zero exit
#     for some other reason is a FAIL of the demonstration, not a pass;
#   - captured output is matched with here-strings, never `printf | grep -q`,
#     which races with pipefail under load (see the compose demo's header).
#
# Cases D1–D4 are the four the brief names:
#   D1 a hand-asserted VERIFIED with no evidence — three spellings: a record with
#      no evidence file, a section source that sets the status, a hand-edited
#      features.json;
#   D2 evidence whose verdict SHA does not match the verified head;
#   D3 an IMPLEMENTED whose merge SHA is not on main (online: needs `gh`);
#   D4 an unknown status.
# D5 shows the floors refusing a component half recorded as the whole
# requirement. G0/G1 are the green baselines each red case returns to.

set -uo pipefail

cd "$(dirname "$0")/../../.." || exit 2
ROOT="$PWD"
GEN="docs/evidence/ledger-generator"
REC="$GEN/status_records.json"
FIX_EVID="docs/evidence/warroom/DEMO-FIXTURE-ledger-status-VERIFY.md"
SCRATCH="$(mktemp -d)"
OUT="$SCRATCH/features.json"
PASSED=0
FAILED=0

USER8_HEAD="c2ff4454b28d3b7887d19fdf2f44742ffb7f55da"
USER8_MERGE="7a3a572b5a518a88da4f503ad171956336b11ed5"
USER8_EARLIER="cf053a3f003b251df4c3405edda91560502c458e"  # an earlier head of the same PR; not on main
BULLET_008='Browser-test environment (VZ-FOUND-008): the Playwright harness runs in CI against the production build image on desktop and mobile projects, and a console or network error fails the lane (demonstrated)'
BULLET_007='Fixture corpus (VZ-FOUND-007): the pinned generator reproduces the twelve M0 fixtures byte-identically against the committed sha256 manifest, and a changed fixture fails the manifest check (demonstrated)'

digest() { if command -v shasum >/dev/null; then shasum -a 256 "$1" | cut -d' ' -f1; else sha256sum "$1" | cut -d' ' -f1; fi; }

status_before="$(git status --porcelain)"
cp "$REC" "$SCRATCH/records.orig"
cp "$GEN/s9_ui_design.py" "$SCRATCH/s9.orig"

cleanup() {
  cp "$SCRATCH/records.orig" "$ROOT/$REC"
  cp "$SCRATCH/s9.orig" "$ROOT/$GEN/s9_ui_design.py"
  rm -f "$ROOT/$FIX_EVID"
  rm -rf "$SCRATCH"
}
trap cleanup EXIT

build() { ( cd "$GEN" && python3 build.py "$OUT" ) 2>&1; }

red() {  # red NAME NEEDLE -- command...
  local name="$1" needle="$2"; shift 3
  local out rc
  out="$("$@" 2>&1)"; rc=$?
  if [ "$rc" -ne 0 ] && grep -qF -- "$needle" <<< "$out"; then
    echo "  RED   (as required) $name — exit $rc, named: $needle"
    grep -F -- "$needle" <<< "$out" | sed 's/^/        | /'
    PASSED=$((PASSED + 1))
  else
    echo "  FAIL  $name — expected a non-zero exit naming [$needle], got exit $rc:"
    sed 's/^/        | /' <<< "$out"
    FAILED=$((FAILED + 1))
  fi
}

green() {  # green NAME -- command...
  local name="$1"; shift 2
  local out rc
  out="$("$@" 2>&1)"; rc=$?
  if [ "$rc" -eq 0 ]; then
    echo "  GREEN (as required) $name — exit 0: $(tail -n 1 <<< "$out" | cut -c1-150)"
    PASSED=$((PASSED + 1))
  else
    echo "  FAIL  $name — expected exit 0, got $rc:"
    sed 's/^/        | /' <<< "$out"
    FAILED=$((FAILED + 1))
  fi
}

# mutate FILE PYTHON — apply one edit with python, refuse if the bytes did not change.
mutate() {
  local file="$1" code="$2" before after
  before="$(digest "$file")"
  python3 - "$file" <<< "$code" || { echo "  FAIL  mutation script errored on $file"; FAILED=$((FAILED + 1)); return 1; }
  after="$(digest "$file")"
  echo "  mutation on $file: sha256 $before -> $after"
  if [ "$before" = "$after" ]; then
    echo "  FAIL  the mutation did not change $file; the case cannot be scored"
    FAILED=$((FAILED + 1)); return 1
  fi
}

# The fixture state: one VERIFIED record for a requirement with no ui/api surface
# that exactly one issue schedules, and an evidence file that ENDS with a PASS on
# the recorded head. It is chosen to pass every OFFLINE rule so that each red
# case below differs from a green state by exactly one mutation.
write_fixture_state() {
  cat > "$ROOT/$FIX_EVID" <<EOF
# DEMONSTRATION FIXTURE — written and deleted by docs/evidence/ledger-status/demo.sh.
# Not evidence of anything. It exists only while the demonstration runs.

FINAL VERDICT: PASS (local; CI BLOCKED) — SHA $USER8_HEAD
EOF
  python3 - "$ROOT/$REC" "$USER8_HEAD" "$USER8_MERGE" "$FIX_EVID" "$BULLET_008" <<'PY'
import json, sys
path, head, merge, evid, bullet = sys.argv[1:]
doc = {"schema": 1, "github_owner": "yegamble", "records": [{
    "id": "VZ-FOUND-008", "status": "VERIFIED",
    "rationale": "DEMONSTRATION FIXTURE written by demo.sh; never committed; not a claim.",
    "acceptance": [{"issue": "docs/issues/VZ-ISSUE-001.md", "bullet": bullet}],
    "merges": [{"repo": "vizra-user", "pr": 8, "verified_head": head, "merge_commit": merge,
                "evidence_file": evid}]}]}
with open(path, "w", encoding="utf-8") as fh:
    json.dump(doc, fh, indent=2, ensure_ascii=False); fh.write("\n")
PY
}
cp_fixture() { cp "$ROOT/$REC" "$SCRATCH/records.fixture"; cp "$ROOT/$FIX_EVID" "$SCRATCH/evid.fixture"; }
back_to_fixture() { cp "$SCRATCH/records.fixture" "$ROOT/$REC"; cp "$SCRATCH/evid.fixture" "$ROOT/$FIX_EVID"; }

echo "== G0 the committed tree: generator and regeneration check"
green "G0a generator on the committed records" -- build
green "G0b scripts/check-generated-ledger.sh on the committed tree" -- ./scripts/check-generated-ledger.sh
green "G0c scripts/check-ledger-status-output.py on the committed tree" -- ./scripts/check-ledger-status-output.py

echo "== G1 fixture state: a VERIFIED record that meets every offline rule is admitted"
write_fixture_state; cp_fixture
green "G1 generator admits the fixture record" -- build
if python3 -c 'import json,sys; f=[x for x in json.load(open(sys.argv[1]))["features"] if x["id"]=="VZ-FOUND-008"][0]; sys.exit(0 if (f["implementation_status"],f["verification_status"],f["merge_status"],f["release_status"])==("VERIFIED","VERIFIED_AT_SHA","MERGED","NOT_RELEASED") else 1)' "$OUT"; then
  echo "  GREEN (as required) G1 output carries VERIFIED / VERIFIED_AT_SHA / MERGED / NOT_RELEASED"; PASSED=$((PASSED + 1))
else
  echo "  FAIL  G1 output does not carry the admitted status"; FAILED=$((FAILED + 1))
fi

echo "== D1a hand-asserted VERIFIED: a record that claims VERIFIED with no evidence file"
mutate "$ROOT/$REC" 'import json,sys; p=sys.argv[1]; d=json.load(open(p)); del d["records"][0]["merges"][0]["evidence_file"]; json.dump(d,open(p,"w"),indent=2)' \
  && red "D1a" "VERIFIED with NO EVIDENCE" -- build
back_to_fixture; green "D1a restored" -- build

echo "== D1b hand-asserted VERIFIED: a section source sets the status itself"
mutate "$ROOT/$GEN/s9_ui_design.py" 'import sys; p=sys.argv[1]; open(p,"a").write("\nREQS[-1][\"implementation_status\"] = \"VERIFIED\"\nREQS[-1][\"verification_status\"] = \"VERIFIED_AT_SHA\"\n")' \
  && red "D1b" "HAND-ASSERTED implementation_status 'VERIFIED' in a section source" -- build
cp "$SCRATCH/s9.orig" "$ROOT/$GEN/s9_ui_design.py"; green "D1b restored" -- build

echo "== D1c hand-asserted VERIFIED: features.json edited by hand and COMMITTED (in a scratch copy)"
copy="$SCRATCH/copy"; mkdir -p "$copy"
cp "$SCRATCH/records.orig" "$ROOT/$REC"; rm -f "$ROOT/$FIX_EVID"
git ls-files -z | (cd "$ROOT" && xargs -0 tar -cf -) | tar -xf - -C "$copy"
(
  cd "$copy" && git init -q && git add -A && git -c user.name=demo -c user.email=demo@invalid commit -qm base
) || { echo "  FAIL  could not make the scratch copy"; FAILED=$((FAILED + 1)); }
mutate "$copy/docs/quality/features.json" 'import sys; p=sys.argv[1]; s=open(p,encoding="utf-8").read(); i=s.index("\"id\": \"VZ-FOUND-008\""); j=s.index("\"implementation_status\": \"PLANNED\"", i); s=s[:j]+"\"implementation_status\": \"VERIFIED\""+s[j+len("\"implementation_status\": \"PLANNED\""):]; open(p,"w",encoding="utf-8").write(s)' \
  && (cd "$copy" && git -c user.name=demo -c user.email=demo@invalid commit -qam "hand-assert VERIFIED") \
  && red "D1c output check" "VZ-FOUND-008: STATUS WITHOUT A RECORD" -- bash -c "cd '$copy' && ./scripts/check-ledger-status-output.py" \
  && red "D1c" "GENERATED FILE IS NOT REPRODUCIBLE" -- bash -c "cd '$copy' && ./scripts/check-generated-ledger.sh"
# The output check runs FIRST: the regeneration check leaves the regenerated
# (correct) file in the tree on failure, and the output check would then report
# that the tree differs from HEAD instead of the status it exists to refuse.
(cd "$copy" && git reset -q --hard HEAD~1) && green "D1c restored" -- bash -c "cd '$copy' && ./scripts/check-generated-ledger.sh" \
  && green "D1c output check restored" -- bash -c "cd '$copy' && ./scripts/check-ledger-status-output.py"
back_to_fixture

echo "== D2 evidence whose verdict SHA does not match the verified head"
mutate "$ROOT/$FIX_EVID" "import sys; p=sys.argv[1]; s=open(p,encoding='utf-8').read(); open(p,'w',encoding='utf-8').write(s.replace('$USER8_HEAD','$USER8_EARLIER'))" \
  && red "D2a verdict names another SHA" "VERDICT SHA MISMATCH" -- build
back_to_fixture; green "D2a restored" -- build
mutate "$ROOT/$FIX_EVID" 'import sys; p=sys.argv[1]; open(p,"a",encoding="utf-8").write("\nFINAL VERDICT: FAIL — SHA '"$USER8_HEAD"'\n")' \
  && red "D2b a later FAIL is the final line" "does not END with a PASS verdict" -- build
back_to_fixture; green "D2b restored" -- build
mutate "$ROOT/$REC" 'import json,sys; p=sys.argv[1]; d=json.load(open(p)); d["records"][0]["merges"][0]["evidence_file"]="docs/evidence/warroom/NO-SUCH-VERIFY.md"; json.dump(d,open(p,"w"),indent=2)' \
  && red "D2c evidence file missing" "MISSING EVIDENCE FILE" -- build
back_to_fixture; green "D2c restored" -- build

echo "== D3 an IMPLEMENTED whose merge SHA is not on main (online, gh api)"
if command -v gh >/dev/null 2>&1; then
  mutate "$ROOT/$REC" 'import json,sys; p=sys.argv[1]; d=json.load(open(p)); r=d["records"][0]; r["status"]="IMPLEMENTED"; del r["merges"][0]["evidence_file"]; json.dump(d,open(p,"w"),indent=2)' \
    && green "D3 baseline: IMPLEMENTED on the true merge commit" -- ./scripts/check-ledger-status-remote.py --records "$ROOT/$REC"
  cp "$ROOT/$REC" "$SCRATCH/records.implemented"
  mutate "$ROOT/$REC" "import json,sys; p=sys.argv[1]; d=json.load(open(p)); d['records'][0]['merges'][0]['merge_commit']='$USER8_EARLIER'; json.dump(d,open(p,'w'),indent=2)" \
    && red "D3" "is NOT on yegamble/vizra-user main" -- ./scripts/check-ledger-status-remote.py --records "$ROOT/$REC"
  cp "$SCRATCH/records.implemented" "$ROOT/$REC"
  green "D3 restored" -- ./scripts/check-ledger-status-remote.py --records "$ROOT/$REC"
  back_to_fixture
else
  echo "  BLOCKED D3 — gh is not installed; this case did NOT run and is counted as a FAIL"
  FAILED=$((FAILED + 1))
fi

echo "== D4 an unknown status"
for bad in DONE IN_PROGRESS VERIFIED_AT_SHA; do
  mutate "$ROOT/$REC" "import json,sys; p=sys.argv[1]; d=json.load(open(p)); d['records'][0]['status']='$bad'; json.dump(d,open(p,'w'),indent=2)" \
    && red "D4 status $bad" "status '$bad' is REFUSED" -- build
  back_to_fixture
done
green "D4 restored" -- build

echo "== D5 floors: a component half is not the requirement"
mutate "$ROOT/$REC" 'import json,sys; p=sys.argv[1]; d=json.load(open(p)); r=d["records"][0]; r["id"]="VZ-INSTALL-003"; r["merges"][0]["repo"]="vizra-core"; json.dump(d,open(p,"w"),indent=2)' \
  && red "D5a ui surface with no vizra-user merge" "names no vizra-user merge" -- build
back_to_fixture
mutate "$ROOT/$REC" "import json,sys; p=sys.argv[1]; d=json.load(open(p)); r=d['records'][0]; r['id']='VZ-FOUND-007'; r['acceptance']=[{'issue':'docs/issues/VZ-ISSUE-001.md','bullet':'''$BULLET_007'''}]; json.dump(d,open(p,'w'),indent=2)" \
  && red "D5b a second issue schedules the requirement" "docs/issues/VZ-ISSUE-006.md schedules VZ-FOUND-007" -- build
back_to_fixture; green "D5 restored" -- build

echo "== D6 the three in-process escapes (meta PR #6 verify probes 2c, 2d, 2e), each in the scratch copy"
# Each escape is appended to the LAST section source (s9), the generator is run
# in the copy, and the result is COMMITTED — exactly what a PR carrying the
# escape would present to the lane. Where the generator still writes the
# ledger, the regeneration check is shown to be blind to it (the output is
# reproducible from the tampered sources), and the out-of-process output check
# must go red. Then the copy is reset to its base commit and must be green again.
S9_COPY="$copy/$GEN/s9_ui_design.py"
escape() {  # escape NAME BUILD_EXPECT(0|1) BUILD_NEEDLE OUTPUT_NEEDLE ; section code in $ESCAPE_CODE
  local name="$1" build_expect="$2" build_needle="$3" output_needle="$4"
  mutate "$S9_COPY" 'import os,sys; open(sys.argv[1],"a",encoding="utf-8").write("\n"+os.environ["ESCAPE_CODE"]+"\n")' || return
  if [ "$build_expect" = "1" ]; then
    red "$name: the generator refuses it in-process" "$build_needle" -- bash -c "cd '$copy/$GEN' && python3 build.py ../../quality/features.json"
  else
    green "$name: the generator is defeated in-process (build exits 0)" -- bash -c "cd '$copy/$GEN' && python3 build.py ../../quality/features.json"
    (cd "$copy" && git -c user.name=demo -c user.email=demo@invalid commit -qam "escape $name") \
      || { echo "  FAIL  $name: nothing to commit — the escape did not change the ledger"; FAILED=$((FAILED + 1)); }
    green "$name: the regeneration check is blind to it (reproducible from the tampered source)" -- bash -c "cd '$copy' && ./scripts/check-generated-ledger.sh"
    red "$name: the out-of-process output check refuses it" "$output_needle" -- bash -c "cd '$copy' && ./scripts/check-ledger-status-output.py"
  fi
  (cd "$copy" && git reset -q --hard base-commit)
  green "$name restored" -- bash -c "cd '$copy' && ./scripts/check-ledger-status-output.py"
}
(cd "$copy" && git tag -f base-commit >/dev/null)

export ESCAPE_CODE='REQS[-1]["status"] = "VERIFIED"
REQS[-1]["verified"] = True'
escape "D6a (2c) extra keys" 0 "" "VZ-CONTROLS-001: KEY SET differs from what core.req emits; extra ['status', 'verified']"

export ESCAPE_CODE='class _S(str):
    def __ne__(self, other):
        return False
REQS[-1]["implementation_status"] = _S("VERIFIED")'
escape "D6b-i (2d) str subclass alone" 1 "VZ-CONTROLS-001: HAND-ASSERTED implementation_status 'VERIFIED'" ""

export ESCAPE_CODE='import status as _st
_orig = _st.check_dsl_defaults
_st.check_dsl_defaults = lambda reqs: [e for e in _orig(reqs) if not e.startswith("VZ-CONTROLS-001:")]
class _S(str):
    def __ne__(self, other):
        return False
REQS[-1]["implementation_status"] = _S("VERIFIED")'
escape "D6b-ii (2d) str subclass with the in-process check wrapped away" 0 "" "VZ-CONTROLS-001: STATUS WITHOUT A RECORD"

export ESCAPE_CODE='import status as _st
_orig = _st.check_dsl_defaults
_st.check_dsl_defaults = lambda reqs: [e for e in _orig(reqs) if not e.startswith("VZ-CONTROLS-001:")]
REQS[-1]["implementation_status"] = "VERIFIED"
REQS[-1]["verification_status"] = "VERIFIED_AT_SHA"'
escape "D6c (2e) wrapper around check_dsl_defaults" 0 "" "VZ-CONTROLS-001: STATUS WITHOUT A RECORD"

echo "== D7 a free-text verdict qualifier (meta PR #6 verify FINDING 4)"
back_to_fixture
mutate "$ROOT/$FIX_EVID" "import sys; p=sys.argv[1]; s=open(p,encoding='utf-8').read(); open(p,'w',encoding='utf-8').write(s.replace('PASS (local; CI BLOCKED)','PASS (superseded — FAIL on re-run)'))" \
  && red "D7 PASS (superseded — FAIL on re-run)" "is NOT ALLOWLISTED" -- build
back_to_fixture; green "D7 restored" -- build

echo "== D8 a bullet tagged for another requirement (meta PR #6 verify NIT 2)"
mutate "$ROOT/$REC" 'import json,sys; p=sys.argv[1]; d=json.load(open(p)); d["records"][0]["id"]="VZ-FOUND-007"; json.dump(d,open(p,"w"),indent=2)' \
  && red "D8 VZ-FOUND-007 citing the VZ-FOUND-008 bullet" "the cited bullet does not name VZ-FOUND-007" -- build
back_to_fixture; green "D8 restored" -- build

echo "== cleanup"
cleanup; trap - EXIT
status_after="$(git status --porcelain)"
if [ "$status_before" = "$status_after" ]; then
  echo "  tree restored: git status identical to the start"
else
  echo "  FAIL  the tree was not restored:"; diff <(echo "$status_before") <(echo "$status_after")
  FAILED=$((FAILED + 1))
fi

echo "demo: $PASSED passed, $FAILED failed"
[ "$FAILED" -eq 0 ]
