#!/usr/bin/env python3
"""Snapshot or check env/registry/setup.json against vizra-core's interview.

Usage:
  scripts/snapshot-setup-keys.py <vizra-core checkout> [REV]
      Print {"source_commit", "questions", "compose_keys"} parsed from
      internal/setup/questions.go at REV (default origin/main). Paste the three
      fields into env/registry/setup.json in one edit; setup_reads, unread_keys
      and not_asked are hand-maintained and reviewed.
  scripts/snapshot-setup-keys.py --check <vizra-core checkout> [setup.json]
      Exit 1 unless setup.json's source_commit is a commit that is an ancestor
      of the checkout's origin/main AND parsing questions.go at that commit
      gives exactly the recorded questions and compose_keys.

The parser resolves `Keys: <ident>` through `var <ident> = []string{...}` and
fails loudly on any question whose key list it cannot resolve; it never skips
an entry (a skipped entry once shifted every later question's keys).
"""
import json
import re
import subprocess
import sys


def die(msg):
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def git(root, *args, check=True):
    r = subprocess.run(["git", "-C", root, *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        die(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r


def string_list(text):
    return re.findall(r'"([A-Z][A-Z0-9_]*)"', text)


def parse(src):
    lists = {m.group(1): string_list(m.group(2)) for m in
             re.finditer(r'(?m)^var\s+([A-Za-z_]\w*)\s*=\s*\[\]string\{([^}]*)\}', src)}
    aliases = {m.group(1): m.group(2) for m in
               re.finditer(r'(?m)^var\s+([A-Za-z_]\w*)\s*=\s*([A-Za-z_]\w*)\s*$', src)}
    if "func Questions()" not in src:
        die("questions.go has no func Questions()")
    body = src[src.index("func Questions()"):]
    # Split on question starts so a key list is only ever taken from its own entry.
    starts = list(re.finditer(r'\{ID:\s*"([a-z0-9_]+)"', body))
    if not starts:
        die("func Questions() has no {ID: ...} entries")
    qs = {}
    for i, m in enumerate(starts):
        qid = m.group(1)
        seg = body[m.end():starts[i + 1].start() if i + 1 < len(starts) else len(body)]
        km = re.search(r'\bKeys:\s*(\[\]string\{([^}]*)\}|([A-Za-z_]\w*))', seg)
        if not km:
            die(f"question {qid}: no Keys field found")
        if km.group(3):
            ident = km.group(3)
            if ident not in lists:
                die(f"question {qid}: Keys: {ident} is not a resolvable `var {ident} = []string{{...}}`")
            keys = lists[ident]
        else:
            keys = string_list(km.group(2))
        if not keys:
            die(f"question {qid}: empty or unparseable key list")
        if qid in qs:
            die(f"question {qid}: duplicate id")
        qs[qid] = keys
    ck = aliases.get("ComposeKeys")
    compose = lists.get(ck) if ck else lists.get("ComposeKeys")
    if compose is None:
        die("questions.go declares no resolvable ComposeKeys")
    return qs, compose


def snapshot(root, rev):
    sha = git(root, "rev-parse", "--verify", f"{rev}^{{commit}}").stdout.strip()
    src = git(root, "show", f"{sha}:internal/setup/questions.go").stdout
    qs, compose = parse(src)
    return sha, qs, compose


def main(argv):
    if argv and argv[0] == "--check":
        if len(argv) < 2:
            die("usage: --check <vizra-core checkout> [setup.json]")
        root = argv[1]
        path = argv[2] if len(argv) > 2 else "env/registry/setup.json"
        setup = json.load(open(path, encoding="utf-8"))
        sha = setup.get("source_commit") or ""
        if not re.fullmatch(r"[0-9a-f]{40}", sha):
            die(f"{path}: source_commit {sha!r} is not a full 40-hex SHA")
        if git(root, "cat-file", "-e", f"{sha}^{{commit}}", check=False).returncode:
            die(f"{path}: source_commit {sha} does not exist in vizra-core")
        git(root, "rev-parse", "--verify", "origin/main^{commit}")
        if git(root, "merge-base", "--is-ancestor", sha, "origin/main", check=False).returncode:
            die(f"{path}: source_commit {sha} is not an ancestor of vizra-core origin/main")
        _, qs, compose = snapshot(root, sha)
        bad = False
        if qs != setup.get("questions"):
            bad = True
            rec = setup.get("questions") or {}
            for q in sorted(set(qs) | set(rec)):
                if qs.get(q) != rec.get(q):
                    print(f"MISMATCH question={q} core={qs.get(q)} setup.json={rec.get(q)}", file=sys.stderr)
        if sorted(compose) != sorted(setup.get("compose_keys") or {}):
            bad = True
            print(f"MISMATCH compose_keys core={compose} setup.json={sorted(setup.get('compose_keys') or {})}", file=sys.stderr)
        if bad:
            die(f"{path} does not match questions.go at {sha[:12]}")
        print(f"PASS: {path} matches vizra-core {sha[:12]} (ancestor of origin/main): "
              f"{len(qs)} questions, compose_keys={compose}")
        return 0
    if not argv:
        die("usage: <vizra-core checkout> [REV]")
    sha, qs, compose = snapshot(argv[0], argv[1] if len(argv) > 1 else "origin/main")
    print(json.dumps({"source_commit": sha, "questions": qs, "compose_keys": compose}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
