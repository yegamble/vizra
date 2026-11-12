#!/usr/bin/env python3
"""Print env/registry/setup.json's `questions` block from a vizra-core checkout.

Usage: scripts/snapshot-setup-keys.py <vizra-core checkout>

Reads internal/setup/questions.go (each `{ID: "...", ... Keys: []string{...}`
entry of Questions()) and prints {"source_commit", "questions"} as JSON. Paste
both fields into env/registry/setup.json in one edit; the rest of that file
(setup_reads, unread_keys, not_asked) is hand-maintained and reviewed.
"""
import json
import re
import subprocess
import sys

root = sys.argv[1]
src = open(f"{root}/internal/setup/questions.go", encoding="utf-8").read()
body = src[src.index("func Questions()"):]
qs = {}
for m in re.finditer(r'\{ID:\s*"([a-z0-9_]+)".*?Keys:\s*\[\]string\{([^}]*)\}', body, re.S):
    qs[m.group(1)] = re.findall(r'"([A-Z][A-Z0-9_]*)"', m.group(2))
sha = subprocess.run(["git", "-C", root, "rev-parse", "HEAD"], capture_output=True,
                     text=True, check=True).stdout.strip()
print(json.dumps({"source_commit": sha, "questions": qs}, indent=2))
