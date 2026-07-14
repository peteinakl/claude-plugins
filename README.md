# claude-plugins

A Claude Cowork plugin marketplace maintained by [AI Innovisory](https://aiinnovisory.com). Plugins here are provided freely as base building blocks — general-purpose skills that aren't tied to a specific client engagement.

## Marketplace

- **Name:** `ai-innovisory-plugins`
- **Owner:** AI Innovisory (peter@aiinnovisory.com)

Add it in Claude Code or Cowork:

```
/plugin marketplace add peteinakl/claude-plugins
```

Then install any plugin listed below:

```
/plugin install <plugin-name>@ai-innovisory-plugins
```

## Plugins in this repository

See [PLUGINS.md](./PLUGINS.md) for the running schedule of plugins, their purpose, and release history.

| Plugin | Purpose | Current version |
|---|---|---|
| [ai-innovisory-base-skills](./plugins/ai-innovisory-base-skills) | Standardised general-purpose skills, starting with `research-review` | 0.1.0 |

## Repository structure

```
claude-plugins/
├── .claude-plugin/
│   └── marketplace.json        # marketplace catalog
├── plugins/
│   └── <plugin-name>/
│       ├── .claude-plugin/
│       │   └── plugin.json     # plugin manifest (semver)
│       ├── skills/
│       └── README.md
├── PLUGINS.md                  # running schedule of plugins and purpose
├── LICENSE
└── README.md
```

## Adding a new plugin

1. Create `plugins/<plugin-name>/` with its own `.claude-plugin/plugin.json` starting at version `0.1.0`.
2. Add its components (`skills/`, `commands/`, etc).
3. Add a `README.md` inside the plugin directory.
4. Register it in `.claude-plugin/marketplace.json`.
5. Add a row to `PLUGINS.md`.
6. Run `claude plugin validate .` from the repo root before committing.

## Releasing a new version of an existing plugin

1. Bump `version` in that plugin's `.claude-plugin/plugin.json` (semver: patch for fixes, minor for new skills/features, major for breaking changes).
2. Update the plugin's own `README.md` if behaviour changed.
3. Log the change in `PLUGINS.md` under that plugin's history.
4. Commit with a message in the form `<plugin-name>: vX.Y.Z — summary`.

Do not set `version` in `marketplace.json` — `plugin.json` is the source of truth for version resolution, and a duplicate value there can silently mask updates.

## Licence

MIT — see [LICENSE](./LICENSE).
