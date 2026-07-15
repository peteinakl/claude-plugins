---
name: file-cleanup
description: Finds files in a folder that haven't been modified in 90+ days, previews them for approval, then moves the approved ones into a structured archive subfolder and logs each move in a markdown index.md. Use this whenever the user wants to tidy up, declutter, or archive old files from a folder, e.g. "clean up my Downloads folder", "archive anything I haven't touched in months", "this folder's a mess, get rid of the old stuff", or "what's stale in here". Only scans the top level of the target folder (not subfolders), never moves anything without explicit confirmation, never archives its own index.md, and always protects Claude-specific context files (CLAUDE.md, MEMORY.md, and anything CLAUDE.md references) from being moved regardless of age. Also handles undoing a previous run. Trigger even if the user doesn't say "archive" or "90 days" explicitly, general folder-tidying requests for a specific directory are the signal.
---

# File cleanup

## What this does

Scans one folder for files that haven't been modified in over 90 days, shows the person exactly what it's about to move, and, once they say go, moves those files into a structured `archive/` subfolder and records every move in a markdown index. Nothing gets moved without a preview and an explicit yes; this is a skill that changes the file system, so caution is core to the design, not an afterthought. A previous run can also be undone from that same log.

Two things it deliberately never does: it never archives Claude's own context files (`CLAUDE.md`, `MEMORY.md`, and anything `CLAUDE.md` references), no matter how old they are, since their relevance isn't a function of when they were last edited. And it never opens a file's contents to decide anything, filename, extension, size and last-modified date are enough, which matters especially for video and audio files where reading the bytes would be slow and wasteful for no benefit.

## Step 1: Confirm the target folder

Work out which folder to clean. If the user names one, use it. If they don't, ask rather than guessing, moving files in the wrong folder is a hard thing to undo cleanly. Default to a 90-day threshold without asking about it separately; state the assumption ("I'll archive anything untouched for 90+ days unless you'd rather use a different cutoff") rather than turning it into a second question up front. If their own phrasing already implies a different cutoff ("anything from before this year", "stuff I haven't touched in 6 months"), use that instead.

## Step 2: Scan for stale files

If `<target_dir>` contains a `CLAUDE.md`, first run:

```bash
python3 scripts/find_claude_references.py <target_dir>
```

This reads CLAUDE.md and returns a ready-to-use, comma-separated list of any other files it references by name that actually exist in the folder, so you don't have to read and reason over CLAUDE.md's prose yourself to work that out. Feed its output straight into the scanner's `--extra-exclude`.

Then run the scanner:

```bash
python3 scripts/scan_stale.py <target_dir> --days 90 --extra-exclude "<output from find_claude_references.py, or omit if empty>" --format table
```

This only looks at files sitting directly inside `<target_dir>`, it does not recurse into subfolders, and subfolders themselves are never candidates for archiving. It automatically excludes hidden files, `index.md`, the archive folder itself, and `CLAUDE.md` / `CLAUDE.local.md` / `MEMORY.md` (case-insensitive, regardless of age). `--format table` prints a compact markdown table you can paste straight into the preview in Step 4 instead of a JSON blob you'd have to reformat yourself, worth using by default; fall back to the plain JSON output (drop `--format table`) only if you need the raw fields (e.g. exact byte sizes or ISO timestamps) for something beyond the preview.

Each row carries a couple of caveats worth reading, not just archiving mechanically:

- A note of "placed here recently despite old mtime" means the file's last-modified date is old, but its filesystem metadata changed recently, most often because it was copied or exported into this folder a lot more recently than its content's original date. That's not disqualifying, plenty of legitimately old files get relocated, but it's worth a second look before archiving something the person may still think of as "new."
- `video` / `audio` notes and the `large` flag exist so you don't need to inspect the file to know it's expensive to read; treat them as a reminder, not an invitation, to leave the contents alone.

If the scan comes back empty, tell the person the folder's already clean and stop here.

## Step 3: Work out the archive structure

Look for an existing archive folder inside `<target_dir>` (the default name is `archive`; also check for `_archive`, `Archive`, or `Archived` in case one already exists under a different name). How you file new archives depends on what you find, in this order:

1. **`index.md` already exists in the archive folder.** Read it. Every index.md this skill produces has a `## Filing rules` section near the top, a plain-language paragraph explaining exactly how files get filed, plus a short `<!-- archive-structure: ... -->` marker comment for quick machine detection. If that section is there, use the scheme it describes. If the file exists but has no `## Filing rules` section (it predates this behaviour, or was hand-edited), infer the scheme from the "Archived to" column of existing entries: paths like `2026-07/report.docx` mean year-month, paths grouped under folders like `documents/` or `images/` mean by-type. `move_and_index.py` backfills the missing section automatically in Step 5 once you tell it what you inferred.
2. **Archive folder exists but has no index.md.** Infer the scheme from its subfolder names the same way.
3. **Neither exists, this is the first run.** Default to year-month subfolders (`archive/2026-07/`). If the target folder is already organized in an obviously different way, e.g. it's already split cleanly into type-based subfolders like `contracts/`, `invoices/`, `images/`, a matching by-type scheme may serve the person better. If it's genuinely unclear, ask.

There are two structures `move_and_index.py` can compute for you automatically, `yearmonth` and `type` (documents / spreadsheets / presentations / images / video / audio / archives / other, by extension); pick one of those unless there's a real reason not to. There's deliberately no "mirror original folder structure" option: because scanning only ever looks at the top level of a folder, every candidate file already sits in the same directory with no subfolder path to mirror, offering that as a choice would just be a flat dump wearing a misleading label. If a person wants something genuinely bespoke (e.g. filing by client name pulled from the filename), use `--structure custom` and supply `--rules-text` describing it, and compute each file's `dest_relative` yourself in the manifest rather than relying on the script.

## Step 4: Preview and get explicit confirmation

Before moving anything, show the person the candidate table from Step 2 (or a trimmed version of it if it's long) along with where each file would land in the archive. Then get explicit confirmation before proceeding.

For a short list, offering a structured yes/no or "which of these to skip" question works fine. For anything beyond a handful of files, a multiple-choice question tool isn't the right instrument, it's built for a few discrete options, not picking through dozens of files, so just ask in plain language ("archive all of these except the two spreadsheets?") and take their reply as-is. Do not move files on the assumption that scanning implied consent; the scan and the move are two separate steps on purpose.

If they want to exclude specific files from the batch, drop those from the manifest you build in Step 5 rather than re-running the scan.

## Step 5: Move and log

Build a manifest for the approved files. For the `yearmonth` and `type` structures this is just a JSON array of absolute source paths, `move_and_index.py` works out the destination itself:

```json
["/path/to/old-report.docx", "/path/to/old-photo.png"]
```

For `custom`, or to override the destination for one specific file, use objects instead: `{"source": "...", "dest_relative": "path relative to the archive folder"}`. The two forms can be mixed in the same array.

Write the manifest to a temp file, then run:

```bash
python3 scripts/move_and_index.py <manifest.json> --archive-dir <target_dir>/archive --structure <yearmonth|type|custom> [--rules-text "<plain-language description, required for custom>"]
```

This moves each file, never overwriting an existing file at the destination (it appends `-2`, `-3`, etc. on a name collision), and appends a row per file to `archive/index.md`. index.md always ends up with a `## Filing rules` section: created up front for a new index, or backfilled in place for an existing one that's missing it, with every existing row and any other content left exactly as it was. It only ever appends new rows; existing entries are never rewritten or reordered. If a source file has disappeared since the preview, or a `custom` entry is missing its `dest_relative`, that file is skipped with a warning rather than failing the whole batch.

## Step 6: Report back

Summarize what happened: how many files moved, where the archive lives, and a pointer to `index.md` if they want the full log. If any files were skipped in Step 5, mention that specifically, it's a sign something else is also touching this folder, or that a custom-structure entry needs fixing. Mention that the run can be undone if they change their mind (see below).

## Undoing a previous run

Because `index.md` records the original location of every file it's ever archived, reversing a run doesn't require guesswork:

```bash
python3 scripts/restore_from_index.py --archive-dir <target_dir>/archive --date <YYYY-MM-DD>
```

This restores every entry archived on that date back to its original location (falling back to a `-2`-suffixed name if something new now occupies that spot) and removes those rows from `index.md`, leaving the Filing rules section and any other entries untouched. To restore only specific files rather than a whole day's run, pass `--archived-to "<comma-separated Archived-to paths>"` instead of `--date`. Use this when the person says something like "actually put those back" or "undo that", there's no need to reconstruct the move by hand.

## A note on repeat runs

Because the structure is written out in plain language in `index.md`'s `## Filing rules` section (backed by a short marker comment for quick detection), running this skill again later on the same folder should be consistent with the first run automatically, you don't need to re-ask about structure once it's established, only re-confirm the actual files to move.
