# Medifab

Client-specific Claude Cowork skills for [Medifab](https://medifab.com), maintained by [AI Innovisory](https://aiinnovisory.com). Unlike `ai-innovisory-base-skills`, everything in this plugin is specific to Medifab's context, Charter, and rollout — not intended for general use.

## Skills included

### medifab-role

Interviews a Medifab team member about their role, one question at a time, and generates a concise role-layer profile in markdown, ready to paste into their Claude Project instructions underneath the shared Medifab company profile. Optionally, as a separate tag-on step afterwards, logs a first automation workflow (owner, review step, benefit measure) to its own file — kept out of the Project instructions since it's a one-off governance log, not context needed every conversation.

Trigger it with "help me set up my role", "add my role", or similar during or after the Medifab AI training day.

## Installing

Add the marketplace, then install the plugin:

```
/plugin marketplace add peteinakl/claude-plugins
/plugin install medifab@ai-innovisory-plugins
```

If you previously installed `ai-innovisory-base-skills` for the `medifab-role` skill, uninstall that and install this plugin instead — the skill has moved here as of `ai-innovisory-base-skills` v0.5.0.

## Versioning

This plugin follows semver (`MAJOR.MINOR.PATCH`) in `plugin.json`. See `PLUGINS.md` at the repository root for the release log across all plugins in this marketplace.
