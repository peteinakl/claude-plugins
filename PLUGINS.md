# Plugin schedule

Running log of every plugin in this marketplace, its purpose, and its release history. Update this file whenever a plugin is added or its version is bumped.

## Active plugins

| Plugin | Purpose | Current version | Skills | Added |
|---|---|---|---|---|
| `ai-innovisory-base-skills` | General-purpose base Claude Cowork skills | 0.7.0 | research-review, transcript-clean, file-cleanup | 2026-07-15 |
| `medifab` | Client-specific Claude Cowork skills for Medifab | 0.1.0 | medifab-role | 2026-07-15 |

## Release history

### ai-innovisory-base-skills

| Version | Date | Change |
|---|---|---|
| 0.1.0 | 2026-07-15 | Initial release. Added `research-review` skill (nine-criterion research readiness review with claim-level web verification). |
| 0.2.0 | 2026-07-15 | Added `medifab-role` skill (interviews a Medifab team member and generates their Claude Project role-layer profile). Client-specific to Medifab. |
| 0.3.0 | 2026-07-15 | Reworked `medifab-role`: interview is now strictly one question at a time instead of grouped rounds. The first-automation workflow is no longer part of the role profile — it's an optional tag-on captured after the core interview and saved to its own file, since it's a one-off governance log rather than context needed every conversation. |
| 0.4.0 | 2026-07-15 | Added `transcript-clean` skill (general-purpose). Turns a raw meeting transcript — including Granola's collapsed "Me/Them" multi-speaker export — into a cleaned, attributed transcript plus a separate summary. Includes a batch mode that dispatches one subagent per file for folders of many transcripts. Developed and validated live against a real Granola export. |
| 0.5.0 | 2026-07-15 | Removed `medifab-role` — moved to its own `medifab` plugin, since it's client-specific rather than general-purpose. Anyone who installed this plugin for that skill should install `medifab` instead. |
| 0.6.0 | 2026-07-15 | Added `file-cleanup` skill (general-purpose). Scans the top level of a folder for files unmodified in 90+ days, previews them for approval, then moves approved files into a structured `archive/` subfolder and logs each move in a markdown `index.md`, which always carries a `## Filing rules` section documenting the convention in plain language (backfilled automatically if an existing index is missing one). Always excludes Claude-context files (`CLAUDE.md`, `CLAUDE.local.md`, `MEMORY.md`, plus anything else `CLAUDE.md` references, found deterministically via a bundled reference scanner) from archiving regardless of age, and never inspects file contents to decide anything: scan output flags `media_type`, `large`, and `possibly_recently_added` (old modified date but recently placed in the folder, e.g. a timestamp-preserving copy) from filesystem metadata alone. `move_and_index.py` computes destination paths itself for the `yearmonth` and `type` structures rather than requiring them to be worked out by hand; the previously offered "mirror original folder structure" option was dropped since it's meaningless for a top-level-only scan. A previous run can be undone via a new `restore_from_index.py`, which moves files back to their recorded original location and removes just those rows from the index. |
| 0.7.0 | 2026-07-15 | `file-cleanup`: added a Topic column to `index.md`, a short plain-language note on what a file actually is, not just its name. Populated only for file types where a quick read is cheap and meaningful (plain text, markdown, PDF via `pdftotext`, docx via python-docx), using a new `extract_excerpts.py` that returns a capped excerpt (~1500 characters, first two pages for PDFs) rather than full file contents. Images, video, audio, spreadsheets, and other binaries always get `-` in this column, consistent with the skill's existing rule that archiving decisions never depend on file contents. An existing index.md written before this column existed gets it backfilled automatically, with `-` padded onto every prior row so the table stays a consistent width instead of growing a ragged cell only on new rows; `restore_from_index.py` was updated to parse both the old 5-column and new 6-column row formats. |

### medifab

| Version | Date | Change |
|---|---|---|
| 0.1.0 | 2026-07-15 | Initial release. Split out of `ai-innovisory-base-skills` v0.5.0. Contains `medifab-role`, unchanged in content — only the packaging moved. |
