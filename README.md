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
| [ai-innovisory-base-skills](./plugins/ai-innovisory-base-skills) | General-purpose skills: `research-review`, `transcript-clean`, `file-cleanup` | 0.7.0 |
| [medifab](./plugins/medifab) | Client-specific skills for Medifab: `medifab-role` | 0.1.0 |

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
