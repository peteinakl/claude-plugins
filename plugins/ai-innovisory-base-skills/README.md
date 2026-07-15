# AI Innovisory base skills

Claude Cowork skills, provided freely by [AI Innovisory](https://aiinnovisory.com). Started as a purely general-purpose base layer; now also carries client-specific role-setup skills where a dedicated plugin isn't warranted.

## Skills included

### research-review

Runs a full readiness review of research (pasted text, a document, or a URL) against a nine-criterion rubric: source quality, evidence separation, currency, coverage, traceability, contradictions, decision value, argument quality, and insight depth. Performs claim-by-claim web verification and returns a markdown scorecard with a Ready / Use with caution / Draft only verdict.

Trigger it with prompts like "is this good enough to act on", "is the thinking sound", or "can I take this to the board or client" — or hand it a document, market scan, or brief directly.

### transcript-clean

Cleans up a raw meeting transcript — especially an unlabelled one from Granola, Otter, Fireflies, Zoom, or Teams — into two files: a fully cleaned and attributed transcript, and a separate summary with attendees, discussion, decisions, and action items. Handles Granola's common "Me/Them" export pattern, where several real speakers can be collapsed into one label with no marker for who's talking; splits those on context cues and clearly flags anything it can't confidently attribute rather than guessing. Supports batch mode for a whole folder of transcripts, dispatching one subagent per file so 40 transcripts don't have to be processed serially in one conversation.

Trigger it with prompts like "clean this up", "turn this into minutes", or by pasting in a wall of unlabelled call transcript.

### medifab-role (client-specific: Medifab)

Interviews a Medifab team member about their role, one question at a time, and generates a concise role-layer profile in markdown, ready to paste into their Claude Project instructions underneath the shared Medifab company profile. Optionally, as a separate tag-on step afterwards, logs a first automation workflow (owner, review step, benefit measure) to its own file — this record stays out of the Project instructions since it's a one-off governance log, not context needed every conversation.

Trigger it with "help me set up my role", "add my role", or similar during or after the Medifab AI training day.

## Installing

Add the marketplace, then install the plugin:

```
/plugin marketplace add peteinakl/claude-plugins
/plugin install ai-innovisory-base-skills@ai-innovisory-plugins
```

## Versioning

This plugin follows semver (`MAJOR.MINOR.PATCH`) in `plugin.json`. The version is bumped on every release that changes a skill's behaviour, so installed copies pick up the update. See `PLUGINS.md` at the repository root for the release log across all plugins in this marketplace.
