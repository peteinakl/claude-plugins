# AI Innovisory base skills

Claude Cowork skills, provided freely by [AI Innovisory](https://aiinnovisory.com). Started as a purely general-purpose base layer; now also carries client-specific role-setup skills where a dedicated plugin isn't warranted.

## Skills included

### research-review

Runs a full readiness review of research (pasted text, a document, or a URL) against a nine-criterion rubric: source quality, evidence separation, currency, coverage, traceability, contradictions, decision value, argument quality, and insight depth. Performs claim-by-claim web verification and returns a markdown scorecard with a Ready / Use with caution / Draft only verdict.

Trigger it with prompts like "is this good enough to act on", "is the thinking sound", or "can I take this to the board or client" — or hand it a document, market scan, or brief directly.

### medifab-role (client-specific: Medifab)

Interviews a Medifab team member about their role and generates a concise role-layer profile in markdown, ready to paste into their Claude Project instructions underneath the shared Medifab company profile.

Trigger it with "help me set up my role", "add my role", or similar during or after the Medifab AI training day.

## Installing

Add the marketplace, then install the plugin:

```
/plugin marketplace add peteinakl/claude-plugins
/plugin install ai-innovisory-base-skills@ai-innovisory-plugins
```

## Versioning

This plugin follows semver (`MAJOR.MINOR.PATCH`) in `plugin.json`. The version is bumped on every release that changes a skill's behaviour, so installed copies pick up the update. See `PLUGINS.md` at the repository root for the release log across all plugins in this marketplace.
