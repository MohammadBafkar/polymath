# polymath-author

Author craft for the Polymath marketplace. Tools, references, and skills for the people writing the plugins.

## What it ships

- Skills: `validate-plugin`, `token-budget-report`, `skill-author-critic`.
- Commands: `/new-plugin`, `/new-skill`, `/new-connector`, `/new-command`, `/new-workflow`, `/new-pack`.
- Scaffolders (`bin/`): `new-plugin.sh`, `new-skill.sh`, `new-connector.sh`, `new-command.sh`, `new-workflow.sh`, `new-pack.sh`. Each command above is a thin alias over the matching script. `new-pack.sh` scaffolds a standalone defaults pack — a marketplace of per-scope conventions plugins (org, team, or project archetype) with `apply-defaults` copy-in — outside this catalog.
- References: [`skill-style-guide.md`](references/skill-style-guide.md), [`frontmatter-cheatsheet.md`](references/frontmatter-cheatsheet.md).

## Installation

```bash
claude plugin install polymath-author@polymath
```

## Dependencies

- `polymath-core`

## License

MIT.
