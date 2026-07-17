# claude-plugins

A Claude Cowork plugin marketplace maintained by [AI Innovisory](https://aiinnovisory.com). `ai-innovisory-base-skills` is the free, general-purpose base layer; client-specific work lives in its own dedicated plugin per client.

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
| [ai-innovisory-base-skills](./plugins/ai-innovisory-base-skills) | General-purpose skills: `research-review`, `transcript-clean`, `file-cleanup` | 0.7.1 |
| [medifab](./plugins/medifab) | Client-specific skills for Medifab: `medifab-role` | 0.1.0 |

## Troubleshooting

### Installed plugin shows an old version

Claude Cowork currently pins a custom marketplace plugin to the commit it first cached and does not re-pull the repository, even after uninstalling and re-adding the plugin or the marketplace ([anthropics/claude-code#69020](https://github.com/anthropics/claude-code/issues/69020)). This repository always serves the latest release; you can confirm the current version of any plugin in its `plugin.json` on GitHub.

Until the bug is fixed upstream, refresh manually:

1. Quit Claude completely (Cmd+Q on macOS).
2. In a terminal, delete the plugin caches: `rm -rf ~/.claude/plugins/marketplaces ~/.claude/plugins/cache`
3. Relaunch Claude, remove this marketplace in Settings, re-add it, and reinstall the plugin.

If it still installs the old version, the app holds a further copy under `~/Library/Application Support/Claude`. With the app closed, locate it with `find ~/Library/Application\ Support/Claude -type d -iname '*<plugin-name>*'`, delete the matching plugin cache folders, then repeat step 3.

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

## Licence

MIT — see [LICENSE](./LICENSE).
