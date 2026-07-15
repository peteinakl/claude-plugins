#!/usr/bin/env python3
"""
Scan a folder, top level only, no recursion into subfolders, for files
whose last-modified time is older than a threshold. Used by the file-cleanup
skill to build the candidate list before anything is moved.

Usage:
    python3 scan_stale.py <target_dir> [--days 90] [--archive-name archive] \
        [--extra-exclude "notes.md,glossary.md"] [--large-threshold-mb 50] \
        [--format json|table]

Default output is JSON: a list of objects, one per stale file, with path,
name, mtime_iso, days_old, size_bytes, media_type, large, and
possibly_recently_added. --format table prints a compact markdown table
instead, ready to paste straight into a preview for the user rather than
requiring a reformatting pass over the JSON.

This script only reads filesystem metadata (name, mtime, ctime, size). It
never opens a file to look at its contents, which matters most for big
media files (video, audio) where reading the bytes would be slow and
pointless: name, extension, size and age are already everything needed to
decide whether to archive one. Uses os.scandir() rather than separate
isfile/getmtime/getsize calls so each file costs one stat lookup instead of
three, which matters on networked or cloud-synced mounts.

possibly_recently_added exists because mtime alone can mislead: a file
copied or exported into this folder recently can carry an old mtime from
its source (many copy tools preserve it), and would otherwise look stale
the moment it arrives. ctime reflects when the file's metadata (including
its content, for a plain copy) last changed on this filesystem, so a large
gap between an old mtime and a recent ctime is a signal the file's presence
here is newer than its "last modified" date suggests. This flag doesn't
exclude anything automatically. it's a caveat for the preview, not a
verdict, since the person reviewing it is better placed to judge whether
that matters for a given file.

Exclusions (all silent, not reported as errors):
  - Directories (this is a top-level file scan, not a recursive walk)
  - Hidden files (dotfiles)
  - index.md (case-insensitive), the archive's own manifest
  - The archive folder itself, if it lives inside the target directory
  - Claude-specific context files: CLAUDE.md, CLAUDE.local.md, MEMORY.md
    (case-insensitive) are always excluded, regardless of age. these carry
    project instructions or memory state Claude itself depends on, so
    archiving them on a routine cleanup pass would be actively harmful, not
    just untidy.
  - Anything passed via --extra-exclude (case-insensitive, comma-separated).
    Use find_claude_references.py to build this list from what CLAUDE.md
    actually references, rather than passing it by hand.
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

CLAUDE_PROTECTED_NAMES = {"claude.md", "claude.local.md", "memory.md"}

VIDEO_EXTENSIONS = {
    ".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".webm", ".m4v", ".mpg", ".mpeg",
}
AUDIO_EXTENSIONS = {
    ".mp3", ".wav", ".flac", ".aac", ".m4a", ".ogg", ".wma",
}

# How much fresher ctime has to be than the mtime threshold implies, to flag
# a file as possibly having been placed here more recently than its
# last-modified date suggests. 30 days is deliberately well inside the
# 90-day default so it doesn't fire on ordinary metadata noise.
RECENT_CTIME_WINDOW_DAYS = 30


def media_type_for(name):
    ext = os.path.splitext(name)[1].lower()
    if ext in VIDEO_EXTENSIONS:
        return "video"
    if ext in AUDIO_EXTENSIONS:
        return "audio"
    return None


def human_size(n):
    size = float(n)
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target_dir")
    ap.add_argument("--days", type=int, default=90,
                     help="age threshold in days (default: 90)")
    ap.add_argument("--archive-name", default="archive",
                     help="name of the archive folder to exclude from the scan")
    ap.add_argument("--extra-exclude", default="",
                     help="comma-separated filenames (case-insensitive) to exclude "
                          "in addition to the default Claude-context protected names")
    ap.add_argument("--large-threshold-mb", type=float, default=50,
                     help="size in MB above which a file is flagged 'large' (default: 50)")
    ap.add_argument("--format", choices=["json", "table"], default="json")
    args = ap.parse_args()

    target = os.path.abspath(args.target_dir)
    if not os.path.isdir(target):
        print(json.dumps({"error": f"Not a directory: {target}"}))
        sys.exit(1)

    extra_excluded = {
        name.strip().lower() for name in args.extra_exclude.split(",") if name.strip()
    }
    large_threshold_bytes = args.large_threshold_mb * 1024 * 1024

    now = time.time()
    threshold_seconds = args.days * 86400
    recent_ctime_seconds = RECENT_CTIME_WINDOW_DAYS * 86400
    results = []

    with os.scandir(target) as it:
        entries = sorted(it, key=lambda e: e.name)

    for entry in entries:
        name = entry.name
        if name.startswith("."):
            continue
        if name.lower() == "index.md":
            continue
        if name == args.archive_name:
            continue
        if name.lower() in CLAUDE_PROTECTED_NAMES:
            continue
        if name.lower() in extra_excluded:
            continue

        try:
            if not entry.is_file():
                continue  # top-level only. subfolders are neither scanned nor moved
            st = entry.stat()
        except OSError:
            continue

        mtime = st.st_mtime
        age_seconds = now - mtime
        if age_seconds < threshold_seconds:
            continue

        ctime = st.st_ctime
        possibly_recently_added = (now - ctime) < recent_ctime_seconds

        size_bytes = st.st_size

        results.append({
            "path": os.path.join(target, name),
            "name": name,
            "mtime_iso": datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat(),
            "days_old": round(age_seconds / 86400, 1),
            "size_bytes": size_bytes,
            "media_type": media_type_for(name),
            "large": size_bytes > large_threshold_bytes,
            "possibly_recently_added": possibly_recently_added,
        })

    if args.format == "table":
        if not results:
            print("(no stale files found)")
            return
        lines = ["| File | Days old | Size | Note |", "|---|---|---|---|"]
        for r in results:
            note_bits = []
            if r["possibly_recently_added"]:
                note_bits.append("placed here recently despite old mtime, check before archiving")
            if r["media_type"]:
                note_bits.append(r["media_type"])
            if r["large"]:
                note_bits.append("large")
            note = "; ".join(note_bits) if note_bits else ""
            lines.append(
                f"| {r['name']} | {r['days_old']} | {human_size(r['size_bytes'])} | {note} |"
            )
        print("\n".join(lines))
    else:
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
