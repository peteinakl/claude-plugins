#!/usr/bin/env python3
"""
Undo a previous file-cleanup archive run: move files back from an archive
folder to the original locations recorded for them in index.md, and remove
those rows from the table.

Usage:
    python3 restore_from_index.py --archive-dir <path> --date 2026-07-15
    python3 restore_from_index.py --archive-dir <path> --archived-to "2026-07/report.docx,images/photo.png"

Exactly one of --date or --archived-to selects which entries to restore.
--date restores every row whose "Archived date" matches (the natural choice
for "undo the run I just did"). --archived-to takes a comma-separated list
of "Archived to" values (paths relative to --archive-dir) for restoring a
specific subset instead.

This only understands the table format move_and_index.py produces: the
"| Archived date | Original location | Archived to | Last modified | Size |"
header row followed by one row per archived file. A heavily hand-edited
index.md may not parse cleanly; if a row looks malformed it's silently
skipped rather than guessed at.

Safety:
  - If the original location is already occupied by something else (e.g. a
    new file was created there since archiving), restores to a "-2"-suffixed
    name instead of overwriting, same collision handling as archiving uses.
  - Skips (with a stderr warning) any archived file that's already missing,
    rather than failing the whole batch.
  - Only removes the specific rows that were actually restored. Everything
    else in index.md, including the Filing rules section, is left as-is.
"""
import argparse
import os
import shutil
import sys


def parse_index_table(content):
    """Parse the archive table, tolerating both the 5-column format (before
    the Topic column existed) and the current 6-column one, so restoring
    works regardless of when a given row was written."""
    lines = content.splitlines()
    header_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("| Archived date"):
            header_idx = i
            break
    if header_idx is None:
        return [], lines

    rows = []
    for i in range(header_idx + 2, len(lines)):
        stripped = lines[i].strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) not in (5, 6):
            continue
        rows.append({
            "line_index": i,
            "archived_date": cells[0],
            "original_path": cells[1],
            "archived_to": cells[2],
            "last_modified": cells[3],
            "size": cells[4],
            "topic": cells[5] if len(cells) == 6 else "-",
        })
    return rows, lines


def unique_dest(dest):
    if not os.path.exists(dest):
        return dest
    base, ext = os.path.splitext(dest)
    n = 2
    while os.path.exists(f"{base}-{n}{ext}"):
        n += 1
    return f"{base}-{n}{ext}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive-dir", required=True)
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--date", help="restore every row archived on this date (YYYY-MM-DD)")
    group.add_argument("--archived-to",
                        help="comma-separated 'Archived to' paths (relative to --archive-dir)")
    args = ap.parse_args()

    archive_dir = os.path.abspath(args.archive_dir)
    index_path = os.path.join(archive_dir, "index.md")
    if not os.path.isfile(index_path):
        print(f"No index.md found at {index_path}", file=sys.stderr)
        sys.exit(1)

    with open(index_path) as f:
        content = f.read()

    rows, lines = parse_index_table(content)
    if not rows:
        print("No archive entries found in index.md.")
        return

    if args.date:
        targets = [r for r in rows if r["archived_date"] == args.date]
    else:
        wanted = {p.strip() for p in args.archived_to.split(",") if p.strip()}
        targets = [r for r in rows if r["archived_to"] in wanted]

    if not targets:
        print("No matching entries found to restore.")
        return

    restored_line_indexes = set()
    restored_count = 0

    for row in targets:
        src = os.path.join(archive_dir, row["archived_to"])
        if not os.path.isfile(src):
            print(f"SKIP (archived file no longer exists): {src}", file=sys.stderr)
            continue

        dest = row["original_path"]
        if os.path.exists(dest):
            new_dest = unique_dest(dest)
            print(f"NOTE: original location occupied, restoring to {new_dest} instead",
                  file=sys.stderr)
            dest = new_dest

        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.move(src, dest)
        print(f"Restored: {src} -> {dest}")
        restored_line_indexes.add(row["line_index"])
        restored_count += 1

    if restored_count == 0:
        print("Nothing restored.")
        return

    new_lines = [line for i, line in enumerate(lines) if i not in restored_line_indexes]
    trailing_newline = "\n" if content.endswith("\n") else ""
    with open(index_path, "w") as f:
        f.write("\n".join(new_lines) + trailing_newline)

    plural = "y" if restored_count == 1 else "ies"
    print(f"Restored {restored_count} file{'s' if restored_count != 1 else ''}, "
          f"removed {restored_count} entr{plural} from index.md")


if __name__ == "__main__":
    main()
