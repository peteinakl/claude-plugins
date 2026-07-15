# AI Innovisory base skills

Claude Cowork skills, provided freely by [AI Innovisory](https://aiinnovisory.com) — the general-purpose base layer every AI Innovisory Cowork setup starts from. Client-specific skills live in their own dedicated plugins (e.g. [`medifab`](../medifab)), not here.

## Skills included

### research-review

Runs a full readiness review of research (pasted text, a document, or a URL) against a nine-criterion rubric: source quality, evidence separation, currency, coverage, traceability, contradictions, decision value, argument quality, and insight depth. Performs claim-by-claim web verification and returns a markdown scorecard with a Ready / Use with caution / Draft only verdict.

Trigger it with prompts like "is this good enough to act on", "is the thinking sound", or "can I take this to the board or client" — or hand it a document, market scan, or brief directly.

### transcript-clean

Cleans up a raw meeting transcript — especially an unlabelled one from Granola, Otter, Fireflies, Zoom, or Teams — into two files: a fully cleaned and attributed transcript, and a separate summary with attendees, discussion, decisions, and action items. Handles Granola's common "Me/Them" export pattern, where several real speakers can be collapsed into one label with no marker for who's talking; splits those on context cues and clearly flags anything it can't confidently attribute rather than guessing. Supports batch mode for a whole folder of transcripts, dispatching one subagent per file so 40 transcripts don't have to be processed serially in one conversation.

Trigger it with prompts like "clean this up", "turn this into minutes", or by pasting in a wall of unlabelled call transcript.

### file-cleanup

Finds files in a folder that haven't been modified in 90+ days, previews the list for approval, then moves the approved files into a structured `archive/` subfolder and logs every move in a markdown `index.md`. Only scans the top level of the target folder, subfolders are left alone. Nothing is moved without explicit confirmation, `index.md` is never itself archived, and Claude's own context files (`CLAUDE.md`, `MEMORY.md`, anything `CLAUDE.md` references) are always protected regardless of age. It never inspects file contents to make a decision, just filename, size, and age, which keeps it cheap even next to large video or audio files, and it flags files that carry an old modified date but were placed in the folder more recently (e.g. a copy that preserved timestamps) so those get a second look before archiving. On repeat runs it reads the archive structure back out of `index.md`'s `## Filing rules` section (year-month by default, or by-type if that's what's already there) so it stays consistent without re-asking, and a previous run can be undone from the same log.

Trigger it with prompts like "clean up my Downloads folder", "archive anything I haven't touched in months", or "this folder's a mess, get rid of the old stuff", naming a folder and wanting it tidied is the signal, not any particular keyword.

## Installing

Add the marketplace, then install the plugin:

```
/plugin marketplace add peteinakl/claude-plugins
/plugin install ai-innovisory-base-skills@ai-innovisory-plugins
```

## Versioning

This plugin follows semver (`MAJOR.MINOR.PATCH`) in `plugin.json`. The version is bumped on every release that changes a skill's behaviour, so installed copies pick up the update. See `PLUGINS.md` at the repository root for the release log across all plugins in this marketplace.
