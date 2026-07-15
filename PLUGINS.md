# Plugin schedule

Running log of every plugin in this marketplace, its purpose, and its release history. Update this file whenever a plugin is added or its version is bumped.

## Active plugins

| Plugin | Purpose | Current version | Skills | Added |
|---|---|---|---|---|
| `ai-innovisory-base-skills` | Base Claude Cowork skills; general-purpose plus select client role-setup skills | 0.4.0 | research-review, medifab-role, transcript-clean | 2026-07-15 |

## Release history

### ai-innovisory-base-skills

| Version | Date | Change |
|---|---|---|
| 0.1.0 | 2026-07-15 | Initial release. Added `research-review` skill (nine-criterion research readiness review with claim-level web verification). |
| 0.2.0 | 2026-07-15 | Added `medifab-role` skill (interviews a Medifab team member and generates their Claude Project role-layer profile). Client-specific to Medifab. |
| 0.3.0 | 2026-07-15 | Reworked `medifab-role`: interview is now strictly one question at a time instead of grouped rounds. The first-automation workflow is no longer part of the role profile — it's an optional tag-on captured after the core interview and saved to its own file, since it's a one-off governance log rather than context needed every conversation. |
| 0.4.0 | 2026-07-15 | Added `transcript-clean` skill (general-purpose). Turns a raw meeting transcript — including Granola's collapsed "Me/Them" multi-speaker export — into a cleaned, attributed transcript plus a separate summary. Includes a batch mode that dispatches one subagent per file for folders of many transcripts. Developed and validated live against a real Granola export. |
