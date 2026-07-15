#!/usr/bin/env python3
"""
Move a confirmed batch of stale files into an archive folder and record each
one in archive/index.md. Used by the file-cleanup skill for the second half
of its workflow, after the user has reviewed and approved the preview list
built from scan_stale.py.

Usage:
    python3 move_and_index.py <manifest.json> --archive-dir <path> \
        --structure <yearmonth|type|custom> [--rules-text "<description>"]

manifest.json is a JSON array built by Claude (not by this script). Each
entry can be either:
  - a plain string: the absolute source path. Used for the "yearmonth" and
    "type" structures, where the destination is fully determined by the
    filename and today's date, there's no judgment call left to make, so
    there's no reason to have an LLM compose that path by hand for
    potentially hundreds of files.
  - an object {"source": "...", "dest_relative": "...", "topic": "..."}:
    dest_relative overrides the computed destination (required for a custom
    structure). topic is optional, a short plain-language description of
    what the file is, written by Claude from an excerpt extracted by
    extract_excerpts.py, never by this script. Leave it out, or use "",
    for files that weren't given a topic (e.g. images, video, audio).

Example:
    ["/abs/path/a.docx",
     {"source": "/abs/path/b.pdf", "topic": "2025 Q3 board deck draft"},
     {"source": "/abs/path/c.psd", "dest_relative": "design-files/c.psd"}]

Why "mirror original folder structure" isn't an option here: this skill
only ever scans the top level of a folder (see scan_stale.py), so every
candidate file already sits in the same directory with no subfolder path of
its own to preserve. A "mirror" scheme would degenerate into dumping
everything straight into the archive root, indistinguishable from having no
structure at all. If a person wants an unusual layout, --structure custom
with explicit dest_relative per file covers it properly instead of offering
a structure option that can't do what it claims.

Every index.md this script produces always has a "## Filing rules" section
near the top, in plain language, so anyone opening the file, human or a
future run of this skill, can see the convention in force without having to
reverse-engineer it from the table rows. If index.md already exists but
predates this section, it gets backfilled in place; existing rows and any
other content are left untouched. The same applies to the Topic column: an
existing index.md written before topics existed gets the column added to
its header and a "-" backfilled onto every existing row, so the table stays
rectangular rather than growing a ragged extra cell only on new rows.

Safety:
  - Creates the archive directory (and any dest subfolders) if missing.
  - Never overwrites an existing file: if the destination already exists,
    appends "-2", "-3", etc. before the extension.
  - Skips (with a stderr warning) any source that no longer exists, or that
    has no resolvable destination, rather than failing the whole batch.
  - Only ever appends new rows to index.md, and only backfills a missing
    Filing rules section, never rewrites or reorders existing rows.
"""
import argparse
import json
import os
import re
import shutil
import sys
from datetime import date, datetime

DEFAULT_RULES = {
    "yearmonth": (
        "Files are filed into subfolders named for the month they're archived in "
        "(`YYYY-MM/`), based on the date each file was moved rather than its "
        "original last-modified date."
    ),
    "type": (
        "Files are filed into subfolders by file type: `documents/`, "
        "`spreadsheets/`, `presentations/`, `images/`, `video/`, `audio/`, "
        "`archives/`, or `other/` for anything that doesn't match a known category."
    ),
}

TYPE_BUCKETS = {
    "documents": {".doc", ".docx", ".pdf", ".txt", ".rtf", ".odt", ".pages", ".md"},
    "spreadsheets": {".xls", ".xlsx", ".csv", ".numbers", ".ods"},
    "presentations": {".ppt", ".pptx", ".key", ".odp"},
    "images": {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".svg", ".heic", ".webp"},
    "video": {".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".webm", ".m4v", ".mpg", ".mpeg"},
    "audio": {".mp3", ".wav", ".flac", ".aac", ".m4a", ".ogg", ".wma"},
    "archives": {".zip", ".tar", ".gz", ".rar", ".7z"},
}


def type_bucket_for(name):
    ext = os.path.splitext(name)[1].lower()
    for bucket, extensions in TYPE_BUCKETS.items():
        if ext in extensions:
            return bucket
    return "other"


def compute_dest_relative(name, structure, archived_date):
    """Return an auto-computed relative destination for known structures, or
    None if the structure requires an explicit dest_relative per file."""
    if structure == "yearmonth":
        return f"{archived_date.strftime('%Y-%m')}/{name}"
    if structure == "type":
        return f"{type_bucket_for(name)}/{name}"
    return None


def unique_dest(dest):
    if not os.path.exists(dest):
        return dest
    base, ext = os.path.splitext(dest)
    n = 2
    while os.path.exists(f"{base}-{n}{ext}"):
        n += 1
    return f"{base}-{n}{ext}"


TOPIC_MAX_LEN = 140


def sanitize_topic(topic):
    """Keep a topic string from breaking the markdown table it lands in."""
    if not topic:
        return "-"
    flat = " ".join(topic.split()).replace("|", "/")
    if len(flat) > TOPIC_MAX_LEN:
        flat = flat[:TOPIC_MAX_LEN - 1].rstrip() + "…"
    return flat


def human_size(n):
    size = float(n)
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def filing_rules_block(structure, rules_text):
    text = rules_text or DEFAULT_RULES.get(
        structure, f"Files are filed using the '{structure}' scheme."
    )
    return (
        "## Filing rules\n\n"
        f"{text.strip()}\n\n"
        f"<!-- archive-structure: {structure} -->\n\n"
    )


def has_filing_rules_section(content):
    return re.search(r"^##\s+Filing rules\b", content, re.IGNORECASE | re.MULTILINE) is not None


def backfill_filing_rules(content, structure, rules_text):
    """Insert a Filing rules section into an existing index.md that lacks one,
    right after the title line, leaving everything else untouched."""
    if has_filing_rules_section(content):
        return content, False

    section = filing_rules_block(structure, rules_text)
    lines = content.splitlines(keepends=True)

    if lines and lines[0].lstrip().startswith("# "):
        insert_at = 1
        if insert_at < len(lines) and lines[insert_at].strip() == "":
            insert_at += 1
        new_content = "".join(lines[:insert_at]) + "\n" + section + "".join(lines[insert_at:])
    else:
        new_content = section + content

    return new_content, True


def has_topic_column(content):
    return re.search(r"^\|\s*Archived date\b.*\bTopic\s*\|", content, re.MULTILINE) is not None


def backfill_topic_column(content):
    """Add a Topic column to an existing index.md that predates it: append it
    to the header and separator rows, and a '-' cell to every existing data
    row, so old and new rows stay the same width instead of the table
    growing a ragged extra cell only on rows written from now on."""
    if has_topic_column(content):
        return content, False

    lines = content.splitlines(keepends=True)
    header_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("| Archived date"):
            header_idx = i
            break
    if header_idx is None:
        return content, False  # no table yet, nothing to migrate

    def append_cell(line, cell_text):
        stripped = line.rstrip("\n")
        newline = "\n" if line.endswith("\n") else ""
        if stripped.rstrip().endswith("|"):
            return stripped.rstrip() + f" {cell_text} |" + newline
        return line

    new_lines = list(lines)
    new_lines[header_idx] = append_cell(lines[header_idx], "Topic")
    if header_idx + 1 < len(lines) and re.match(r"^\|[\s\-|]+\|\s*$", lines[header_idx + 1].strip()):
        new_lines[header_idx + 1] = append_cell(lines[header_idx + 1], "---")
        data_start = header_idx + 2
    else:
        data_start = header_idx + 1
    for i in range(data_start, len(lines)):
        if lines[i].strip().startswith("|"):
            new_lines[i] = append_cell(lines[i], "-")

    return "".join(new_lines), True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest", help="path to the manifest JSON file")
    ap.add_argument("--archive-dir", required=True)
    ap.add_argument("--structure", default="yearmonth",
                     help="scheme in use: yearmonth, type, or custom")
    ap.add_argument("--rules-text", default=None,
                     help="plain-language description of the filing rule for the "
                          "Filing rules section; defaults to stock wording for "
                          "yearmonth/type, required for anything else")
    args = ap.parse_args()

    with open(args.manifest) as f:
        manifest = json.load(f)

    archive_dir = os.path.abspath(args.archive_dir)
    os.makedirs(archive_dir, exist_ok=True)
    index_path = os.path.join(archive_dir, "index.md")
    is_new_index = not os.path.exists(index_path)
    today = date.today()

    rows = []
    for item in manifest:
        if isinstance(item, str):
            src, dest_rel, topic = item, None, None
        else:
            src = item["source"]
            dest_rel = item.get("dest_relative")
            topic = item.get("topic") or None

        if not os.path.isfile(src):
            print(f"SKIP (source no longer exists): {src}", file=sys.stderr)
            continue

        if dest_rel is None:
            dest_rel = compute_dest_relative(os.path.basename(src), args.structure, today)
        if dest_rel is None:
            print(
                f"SKIP (no dest_relative given, and structure '{args.structure}' "
                f"can't be auto-computed): {src}",
                file=sys.stderr,
            )
            continue

        dest = unique_dest(os.path.join(archive_dir, dest_rel))
        os.makedirs(os.path.dirname(dest), exist_ok=True)

        mtime = os.path.getmtime(src)
        size = os.path.getsize(src)
        shutil.move(src, dest)

        rows.append({
            "archived_date": today.isoformat(),
            "original_path": src,
            "archived_to": os.path.relpath(dest, archive_dir),
            "last_modified": datetime.fromtimestamp(mtime).date().isoformat(),
            "size": human_size(size),
            "topic": sanitize_topic(topic),
        })
        print(f"Moved: {src} -> {dest}")

    if is_new_index:
        header = "# Archive index\n\n"
        header += filing_rules_block(args.structure, args.rules_text)
        header += (
            "Files below were moved here by the file-cleanup skill because they "
            "hadn't been modified in 90+ days. This file is the manifest for the "
            "archive, it is never itself moved or archived.\n\n"
        )
        header += "| Archived date | Original location | Archived to | Last modified | Size | Topic |\n"
        header += "|---|---|---|---|---|---|\n"
        with open(index_path, "w") as f:
            f.write(header)
    else:
        with open(index_path) as f:
            existing = f.read()
        updated, rules_changed = backfill_filing_rules(existing, args.structure, args.rules_text)
        updated, topic_changed = backfill_topic_column(updated)
        if rules_changed or topic_changed:
            with open(index_path, "w") as f:
                f.write(updated)
            if rules_changed:
                print("Backfilled a missing 'Filing rules' section into the existing index.md")
            if topic_changed:
                print("Backfilled a missing Topic column into the existing index.md")

    if not rows:
        print("No files moved.")
        return

    with open(index_path, "a") as f:
        for r in rows:
            f.write(
                f"| {r['archived_date']} | {r['original_path']} | {r['archived_to']} "
                f"| {r['last_modified']} | {r['size']} | {r['topic']} |\n"
            )

    print(f"Updated index: {index_path} ({len(rows)} entries added)")


if __name__ == "__main__":
    main()
