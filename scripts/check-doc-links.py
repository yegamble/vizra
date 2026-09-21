#!/usr/bin/env python3
"""Relative markdown links in docs/ and the root *.md must resolve to a file
that exists in this repository.

External URLs are NEVER fetched. This check does no network I/O at all: a link
checker that reaches the internet turns a documentation lane into a flaky one
and into an egress path, and neither belongs in a required gate. `http:`,
`https:`, `mailto:` and `tel:` targets are recorded and skipped.

**Code is not prose.** Fenced blocks and inline code spans are stripped before
any link is matched. Without that, a naive scan of this repository reports 26
broken links, all 26 of them false positives from inline code such as
`globalThis["fetch"](url, init)` — text that a markdown renderer never treats
as a link. A check that cries wolf 26 times is a check people turn off.

**The nested component checkouts are not part of this repository.**
`vizra-core/`, `vizra-user/` and `vizra-search/` are gitignored checkouts
(docs/META_REPO.md §1). They exist on a developer's machine and do NOT exist on
a CI runner, so a link into one would be green locally and red in CI. Such a
link is refused by name with that explanation rather than being resolved
against whatever happens to be on disk.

Exit codes:
    0  clean
    1  at least one relative link does not resolve, each named with its source
       file and line
"""

import glob
import os
import re
import sys

DOC_GLOBS = ["docs/**/*.md", "*.md"]

# Checkouts that are gitignored and absent in CI (docs/META_REPO.md §1).
NESTED_CHECKOUTS = ("vizra-core", "vizra-user", "vizra-search")

EXTERNAL_SCHEMES = ("http://", "https://", "mailto:", "tel:", "ftp://")

FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
# Inline code spans. Deliberately confined to ONE line: an unmatched backtick
# must not be able to pair with one several paragraphs later and blank out real
# links in between. Every false positive in this repository is single-line.
INLINE_CODE = re.compile(r"(?P<ticks>`+)[^\n]*?(?P=ticks)")
# [text](target "optional title") — target may be <bracketed>.
INLINE_LINK = re.compile(r"\[(?:[^\]\\]|\\.)*\]\(\s*(<[^>]*>|[^\s)]*)(?:\s+[^)]*)?\)")
# [id]: target "optional title"  at the start of a line.
REF_DEFINITION = re.compile(r"^\s{0,3}\[(?:[^\]\\]|\\.)+\]:\s*(<[^>]*>|\S+)")


def strip_code(text):
    """Blank out fenced blocks and inline code spans, preserving line numbers.

    Replacement is space-for-character (newlines kept) so every surviving link
    still reports the line it is really on.
    """
    out_lines = []
    fence_marker = None
    for line in text.split("\n"):
        match = FENCE.match(line)
        if fence_marker is None:
            if match:
                fence_marker = match.group(1)[0] * 3
                out_lines.append("")
                continue
            out_lines.append(line)
        else:
            # A closing fence is at least as long as the opener and of the same char.
            if match and match.group(1)[0] * 3 == fence_marker:
                fence_marker = None
            out_lines.append("")
    stripped = "\n".join(out_lines)
    return INLINE_CODE.sub(lambda m: " " * len(m.group(0)), stripped)


def targets(text):
    """Yield (line_number, raw_target) for every markdown link target."""
    for match in INLINE_LINK.finditer(text):
        yield text.count("\n", 0, match.start()) + 1, match.group(1)
    for match in REF_DEFINITION.finditer(text):
        yield text.count("\n", 0, match.start()) + 1, match.group(1)


def main():
    paths = []
    for pattern in DOC_GLOBS:
        matched = sorted(glob.glob(pattern, recursive=True))
        if not matched:
            sys.stderr.write(
                f"NO FILES MATCHED '{pattern}' — the link check would verify nothing\n"
            )
            return 1
        paths.extend(matched)

    broken = []
    checked = 0
    external = 0

    for path in paths:
        try:
            with open(path, "r", encoding="utf-8") as handle:
                text = handle.read()
        except OSError as err:
            sys.stderr.write(f"UNREADABLE: {path}: {err}\n")
            return 1

        for line_no, raw in targets(strip_code(text)):
            target = raw.strip()
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1].strip()
            if not target or target.startswith("#"):
                continue
            if target.lower().startswith(EXTERNAL_SCHEMES) or target.startswith("//"):
                external += 1
                continue

            # Drop the fragment and query; a file link's anchor is not checked here.
            file_part = target.split("#", 1)[0].split("?", 1)[0]
            if not file_part:
                continue
            try:
                file_part = _unescape(file_part)
            except ValueError:
                broken.append((path, line_no, target, "target is not a usable path"))
                continue

            if file_part.startswith("/"):
                resolved = os.path.normpath(file_part.lstrip("/"))
            else:
                resolved = os.path.normpath(os.path.join(os.path.dirname(path), file_part))

            checked += 1

            first = resolved.split(os.sep, 1)[0]
            if first in NESTED_CHECKOUTS:
                broken.append(
                    (
                        path,
                        line_no,
                        target,
                        f"points into the gitignored '{first}/' checkout, which does not "
                        "exist on a CI runner (docs/META_REPO.md §1)",
                    )
                )
                continue
            if resolved.startswith(".."):
                broken.append((path, line_no, target, "escapes the repository root"))
                continue
            if not os.path.exists(resolved):
                broken.append((path, line_no, target, f"'{resolved}' does not exist"))

    if broken:
        sys.stderr.write(f"BROKEN RELATIVE LINK(S): {len(broken)}\n")
        for path, line_no, target, why in broken:
            sys.stderr.write(f"  {path}:{line_no}: [{target}] — {why}\n")
        return 1

    # Anti-false-green. This repository currently contains ZERO relative markdown
    # links — every link-shaped string in docs/ is either inside code (26 of them)
    # or an external URL (6). So `checked == 0` is the honest state today and must
    # not be reported as if links had been verified. What must never happen
    # silently is the matcher finding NOTHING AT ALL, which is what a broken regex
    # or an over-eager code stripper looks like from outside.
    if checked + external == 0:
        sys.stderr.write(
            "NO LINK OF ANY KIND MATCHED across "
            f"{len(paths)} markdown file(s) — neither relative nor external.\n"
            "  That is not a clean repository, it is a checker that has stopped matching.\n"
        )
        return 1

    if checked == 0:
        print(
            f"relative links: none exist yet across {len(paths)} markdown file(s) "
            f"(checked nothing); {external} external URL(s) recorded and not fetched"
        )
    else:
        print(
            f"relative links: {checked} checked across {len(paths)} markdown file(s), "
            f"all resolve; {external} external URL(s) recorded and not fetched"
        )
    return 0


def _unescape(part):
    """Undo markdown backslash escapes and percent-encoding in a path."""
    part = re.sub(r"\\([\\`*_{}\[\]()#+\-.!])", r"\1", part)
    if "%" in part:
        from urllib.parse import unquote

        part = unquote(part)
    if "\x00" in part:
        raise ValueError("NUL in path")
    return part


if __name__ == "__main__":
    sys.exit(main())
