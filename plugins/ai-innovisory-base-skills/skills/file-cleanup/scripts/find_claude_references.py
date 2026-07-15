#!/usr/bin/env python3
"""
Find files inside target_dir that CLAUDE.md references by name, so
scan_stale.py can be told to protect them via --extra-exclude alongside the
default CLAUDE.md / CLAUDE.local.md / MEMORY.md protection.

Usage:
    python3 find_claude_references.py <target_dir>

Prints a comma-separated list of matching filenames to stdout (empty string
if there's no CLAUDE.md, or it references nothing that's actually present).

Why this exists instead of just having Claude read CLAUDE.md and reason
about what it mentions: that works, but it's a judgment call standing in
for something that should be deterministic, and prose is easy to skim past
an indirect reference ("see the memory file" without naming it). This
script instead extracts every filename-shaped token from CLAUDE.md via
regex (markdown links, @-mentions, and bare filenames with a handful of
common extensions), then intersects that against what's actually sitting in
target_dir. The intersection step matters: CLAUDE.md might mention
"README.md" as a generic example with no such file present, and reporting
that as something to protect would just be noise. Only names that exist in
the folder are ever returned, so the output is directly usable without
Claude needing to double-check it, and reading CLAUDE.md's prose is no
longer a token cost this workflow has to pay.
"""
import argparse
import os
import re
import sys

# Extensions worth treating as a possible CLAUDE.md reference. Deliberately
# narrow to text/context-file types, not free of e.g. video, since CLAUDE.md
# pointing at a media file by name would be unusual and this is meant to
# catch memory/instruction/reference docs, not everything under the sun.
REFERENCE_EXTENSIONS = {".md", ".txt", ".json", ".yaml", ".yml"}

# Already protected by default in scan_stale.py, no need to report these too.
ALREADY_PROTECTED = {"claude.md", "claude.local.md", "memory.md"}

MARKDOWN_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
AT_MENTION_RE = re.compile(r"@([A-Za-z0-9_\-./]+\.\w+)")
BARE_FILENAME_RE = re.compile(r"\b([A-Za-z0-9_\-]+\.[A-Za-z0-9]+)\b")


def extract_candidate_names(text):
    candidates = set()

    for match in MARKDOWN_LINK_RE.findall(text):
        if match.startswith(("http://", "https://", "#")):
            continue
        candidates.add(os.path.basename(match))

    for match in AT_MENTION_RE.findall(text):
        candidates.add(os.path.basename(match))

    for match in BARE_FILENAME_RE.findall(text):
        candidates.add(match)

    return {
        name for name in candidates
        if os.path.splitext(name)[1].lower() in REFERENCE_EXTENSIONS
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target_dir")
    args = ap.parse_args()

    target = os.path.abspath(args.target_dir)
    claude_md = os.path.join(target, "CLAUDE.md")

    if not os.path.isfile(claude_md):
        print("")
        return

    try:
        with open(claude_md, encoding="utf-8", errors="ignore") as f:
            text = f.read()
    except OSError as e:
        print(f"error reading CLAUDE.md: {e}", file=sys.stderr)
        print("")
        return

    candidates = extract_candidate_names(text)

    # Only report names that actually exist in target_dir, case-insensitive,
    # and never report CLAUDE.md itself (it's already protected separately).
    present = {name.lower(): name for name in os.listdir(target)}
    matches = sorted(
        present[name.lower()]
        for name in candidates
        if name.lower() in present and name.lower() not in ALREADY_PROTECTED
    )

    print(",".join(matches))


if __name__ == "__main__":
    main()
