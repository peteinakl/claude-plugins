#!/usr/bin/env python3
"""
Self-contained tests for the file-cleanup mutation scripts, move_and_index.py
and restore_from_index.py. Everything runs inside throwaway temp directories;
nothing outside them is read or touched, and no third-party packages are
needed.

Run:
    python3 test_file_cleanup.py

Prints one PASS/FAIL line per test and exits non-zero if anything failed.
Covers the two safety properties the skill leans on hardest:

  - Containment: a manifest destination cannot move a file outside the
    archive folder, whether via ".." traversal or an absolute path. The
    manifest is LLM-authored, so the script has to be the backstop.
  - Reversibility: any legal filename that gets archived restores to its
    exact original name from index.md, including names containing pipes.
    Names a line-based log cannot represent (e.g. a newline) are refused at
    move time rather than logged unparseably. Indexes written by older
    versions (5-column, and 6-column before escaping existed) still restore.
"""
import json
import os
import subprocess
import sys
import tempfile

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
MOVE = os.path.join(SCRIPTS_DIR, "move_and_index.py")
RESTORE = os.path.join(SCRIPTS_DIR, "restore_from_index.py")

sys.path.insert(0, SCRIPTS_DIR)
from restore_from_index import parse_index_table, split_row  # noqa: E402


def run(script, *argv):
    return subprocess.run(
        [sys.executable, script, *argv], capture_output=True, text=True
    )


def write(path, text):
    with open(path, "w") as f:
        f.write(text)


def read(path):
    with open(path) as f:
        return f.read()


def move_manifest(tmp, entries, archive_dir, structure="yearmonth", rules_text=None):
    manifest = os.path.join(tmp, "manifest.json")
    with open(manifest, "w") as f:
        json.dump(entries, f)
    argv = [manifest, "--archive-dir", archive_dir, "--structure", structure]
    if rules_text:
        argv += ["--rules-text", rules_text]
    return run(MOVE, *argv)


def index_rows(archive_dir):
    return parse_index_table(read(os.path.join(archive_dir, "index.md")))[0]


def test_traversal_dest_relative_is_refused():
    with tempfile.TemporaryDirectory() as tmp:
        target = os.path.join(tmp, "target")
        victim = os.path.join(tmp, "victim")
        os.makedirs(target)
        os.makedirs(victim)
        src_a = os.path.join(target, "old.docx")
        src_b = os.path.join(target, "old2.txt")
        write(src_a, "secret a")
        write(src_b, "secret b")
        archive = os.path.join(target, "archive")

        result = move_manifest(
            tmp,
            [
                {"source": src_a, "dest_relative": "../../victim/escaped.docx"},
                {"source": src_b, "dest_relative": "../../../escaped-deeper.txt"},
            ],
            archive, structure="custom", rules_text="custom filing",
        )
        assert result.returncode == 0, f"skip-not-fail violated: {result.stderr}"
        assert "outside the archive" in result.stderr, (
            f"expected a containment SKIP warning, got: {result.stderr!r}"
        )
        assert os.path.isfile(src_a) and os.path.isfile(src_b), (
            "refused files must be left in place at their source"
        )
        assert not os.path.exists(os.path.join(victim, "escaped.docx")), (
            "file escaped the archive root via .. traversal"
        )
        assert index_rows(archive) == [], (
            "no index row may be written for a refused move"
        )


def test_absolute_dest_relative_is_refused():
    with tempfile.TemporaryDirectory() as tmp:
        target = os.path.join(tmp, "target")
        os.makedirs(target)
        src = os.path.join(target, "old.txt")
        write(src, "secret")
        archive = os.path.join(target, "archive")
        escape_dest = os.path.join(tmp, "outside", "esc.txt")

        result = move_manifest(
            tmp,
            [{"source": src, "dest_relative": escape_dest}],
            archive, structure="custom", rules_text="custom filing",
        )
        assert result.returncode == 0, f"skip-not-fail violated: {result.stderr}"
        assert "outside the archive" in result.stderr, (
            f"expected a containment SKIP warning, got: {result.stderr!r}"
        )
        assert os.path.isfile(src), "refused file must be left in place"
        assert not os.path.exists(escape_dest), (
            "file escaped the archive root via an absolute dest_relative"
        )
        assert index_rows(archive) == [], (
            "no index row may be written for a refused move"
        )


def test_pipe_filename_archives_and_restores():
    with tempfile.TemporaryDirectory() as tmp:
        target = os.path.join(tmp, "target")
        os.makedirs(target)
        src = os.path.join(target, "report|final.txt")
        write(src, "pipe file contents")
        archive = os.path.join(target, "archive")

        result = move_manifest(tmp, [src], archive)
        assert result.returncode == 0, result.stderr
        assert not os.path.exists(src), "file should have been archived"

        content = read(os.path.join(archive, "index.md"))
        assert "report\\|final.txt" in content, (
            "pipe in the filename must be written escaped"
        )
        data_lines = [
            line for line in content.splitlines()
            if line.startswith("| ") and not line.startswith("| Archived date")
        ]
        assert len(data_lines) == 1, f"expected one data row, got {len(data_lines)}"
        parts = split_row(data_lines[0])
        assert len(parts) == 8 and not parts[0].strip() and not parts[-1].strip(), (
            f"row must be well-formed with exactly 6 columns, got {len(parts) - 2}"
        )

        rows = index_rows(archive)
        assert len(rows) == 1, f"parser must see exactly one row, got {len(rows)}"
        row = rows[0]
        assert row["original_path"] == src, (
            f"original path must round-trip exactly, got {row['original_path']!r}"
        )
        assert os.path.isfile(os.path.join(archive, row["archived_to"])), (
            "archived_to must point at the real archived file"
        )

        result = run(RESTORE, "--archive-dir", archive, "--date", row["archived_date"])
        assert result.returncode == 0, result.stderr
        assert os.path.isfile(src), (
            "file must restore to its exact original piped name"
        )
        assert read(src) == "pipe file contents", "contents must survive the round trip"
        assert index_rows(archive) == [], "restored row must be removed from the index"


def test_collision_gets_numbered_suffix():
    with tempfile.TemporaryDirectory() as tmp:
        target = os.path.join(tmp, "target")
        os.makedirs(target)
        archive = os.path.join(target, "archive")
        occupied = os.path.join(archive, "documents", "dup.txt")
        os.makedirs(os.path.dirname(occupied))
        write(occupied, "already here")
        src = os.path.join(target, "dup.txt")
        write(src, "new arrival")

        result = move_manifest(tmp, [src], archive, structure="type")
        assert result.returncode == 0, result.stderr
        assert read(occupied) == "already here", (
            "existing file at the destination must never be overwritten"
        )
        suffixed = os.path.join(archive, "documents", "dup-2.txt")
        assert os.path.isfile(suffixed), "collision must produce a -2 suffixed name"
        assert read(suffixed) == "new arrival"
        rows = index_rows(archive)
        assert len(rows) == 1 and rows[0]["archived_to"] == "documents/dup-2.txt", (
            f"index must record the suffixed destination, got {rows!r}"
        )


def test_round_trip_removes_only_its_row():
    with tempfile.TemporaryDirectory() as tmp:
        target = os.path.join(tmp, "target")
        os.makedirs(target)
        src_keep = os.path.join(target, "keep.txt")
        src_undo = os.path.join(target, "undo.txt")
        write(src_keep, "stays archived")
        write(src_undo, "comes back")
        archive = os.path.join(target, "archive")

        result = move_manifest(tmp, [src_keep, src_undo], archive)
        assert result.returncode == 0, result.stderr
        rows = index_rows(archive)
        assert len(rows) == 2, f"expected two archived rows, got {len(rows)}"
        undo_row = next(r for r in rows if r["original_path"] == src_undo)

        result = run(
            RESTORE, "--archive-dir", archive, "--archived-to", undo_row["archived_to"]
        )
        assert result.returncode == 0, result.stderr
        assert os.path.isfile(src_undo) and read(src_undo) == "comes back", (
            "restored file must be back at its original location"
        )
        assert not os.path.exists(src_keep), "the other file must stay archived"

        content = read(os.path.join(archive, "index.md"))
        rows = parse_index_table(content)[0]
        assert len(rows) == 1 and rows[0]["original_path"] == src_keep, (
            "only the restored file's row may be removed"
        )
        assert "## Filing rules" in content, "Filing rules section must survive undo"
        assert "<!-- archive-structure: yearmonth -->" in content, (
            "structure marker must survive undo"
        )


def test_old_format_indexes_still_restore():
    # 5-column era: written before the Topic column or escaping existed.
    with tempfile.TemporaryDirectory() as tmp:
        target = os.path.join(tmp, "target")
        os.makedirs(target)
        archive = os.path.join(target, "archive")
        os.makedirs(os.path.join(archive, "2026-01"))
        write(os.path.join(archive, "2026-01", "notes.txt"), "five-column era")
        original = os.path.join(target, "notes.txt")
        write(os.path.join(archive, "index.md"), (
            "# Archive index\n\n"
            "## Filing rules\n\n"
            "Files are filed into subfolders named for the month they're "
            "archived in (`YYYY-MM/`).\n\n"
            "<!-- archive-structure: yearmonth -->\n\n"
            "| Archived date | Original location | Archived to | Last modified | Size |\n"
            "|---|---|---|---|---|\n"
            f"| 2026-01-10 | {original} | 2026-01/notes.txt | 2025-09-01 | 1.0 KB |\n"
        ))
        result = run(RESTORE, "--archive-dir", archive, "--date", "2026-01-10")
        assert result.returncode == 0, result.stderr
        assert os.path.isfile(original) and read(original) == "five-column era", (
            "old 5-column index must still restore"
        )
        assert index_rows(archive) == [], "restored row must be removed"

    # 6-column era: Topic column present, but paths written raw (pre-escaping).
    with tempfile.TemporaryDirectory() as tmp:
        target = os.path.join(tmp, "target")
        os.makedirs(target)
        archive = os.path.join(target, "archive")
        os.makedirs(os.path.join(archive, "2026-06"))
        write(os.path.join(archive, "2026-06", "plan.md"), "six-column era")
        original = os.path.join(target, "plan.md")
        write(os.path.join(archive, "index.md"), (
            "# Archive index\n\n"
            "## Filing rules\n\n"
            "Files are filed into subfolders named for the month they're "
            "archived in (`YYYY-MM/`).\n\n"
            "<!-- archive-structure: yearmonth -->\n\n"
            "| Archived date | Original location | Archived to | Last modified | Size | Topic |\n"
            "|---|---|---|---|---|---|\n"
            f"| 2026-06-02 | {original} | 2026-06/plan.md | 2025-12-01 | 2.1 KB | Draft rollout plan |\n"
        ))
        result = run(RESTORE, "--archive-dir", archive, "--date", "2026-06-02")
        assert result.returncode == 0, result.stderr
        assert os.path.isfile(original) and read(original) == "six-column era", (
            "old raw 6-column index must still restore"
        )
        assert index_rows(archive) == [], "restored row must be removed"


def test_control_character_name_is_refused():
    with tempfile.TemporaryDirectory() as tmp:
        target = os.path.join(tmp, "target")
        os.makedirs(target)
        src = os.path.join(target, "bad\nname.txt")
        write(src, "unrepresentable")
        archive = os.path.join(target, "archive")

        result = move_manifest(tmp, [src], archive)
        assert result.returncode == 0, f"skip-not-fail violated: {result.stderr}"
        assert "control character" in result.stderr, (
            f"expected a control-character SKIP warning, got: {result.stderr!r}"
        )
        assert os.path.isfile(src), (
            "a name index.md cannot record must be left in place, not moved"
        )
        assert index_rows(archive) == [], "no row may be written for a refused move"


TESTS = [
    test_traversal_dest_relative_is_refused,
    test_absolute_dest_relative_is_refused,
    test_pipe_filename_archives_and_restores,
    test_collision_gets_numbered_suffix,
    test_round_trip_removes_only_its_row,
    test_old_format_indexes_still_restore,
    test_control_character_name_is_refused,
]


def main():
    failed = 0
    for test in TESTS:
        try:
            test()
        except AssertionError as e:
            failed += 1
            print(f"FAIL {test.__name__}: {e}")
        except Exception as e:  # a crashed test is a failed test
            failed += 1
            print(f"FAIL {test.__name__}: unexpected error: {e!r}")
        else:
            print(f"PASS {test.__name__}")

    if failed:
        print(f"\n{failed} of {len(TESTS)} tests failed")
        sys.exit(1)
    print(f"\nAll {len(TESTS)} tests passed")


if __name__ == "__main__":
    main()
