---
name: conventions
description: Load Polymath project conventions (commit style, PR shape, plugin layout) when starting a task that touches the marketplace.
---

# conventions

> Polymath project conventions that apply across plugins. Load this when starting any task that touches plugin authoring, marketplace structure, or contribution flow.

## When to use

- The user mentions "conventions", "house rules", "the Polymath way".
- A workflow step needs to ground itself in marketplace standards.
- A new contributor is being onboarded.

## Conventions

### Naming

- Plugins: `polymath-<bare-name>` (kebab-case).
- Skills/commands: bare file names. Invocation is namespaced (`/polymath-product:prd`).
- Agents: nouns-of-people (`security-reviewer`, `pm-critic`).
- Templates: PascalCase artifact names (`PRD.md`, `ADR.md`).
- Workflows: camelCase (`shipFeature.yaml`).

### Token budget

- Per-plugin always-on listing ≤ 400 tokens.
- MVP total ≤ 1,500 tokens measured.
- Descriptions ≤ 200 chars, trigger phrase first.
- SKILL.md ≤ 500 lines.

### Commands vs skills

- Skill when bundling templates / scripts / references.
- Command for thin aliases (≤ 20 lines).
- If both exist for the same name, command is a thin alias pointing to the skill.

### Hooks

Hooks are deterministic gates. They never block silently — every block produces a user-visible reason. Hook scripts live in `hooks/scripts/`.

### Workflows

- Schema: `shared/schemas/workflow.schema.json`.
- Resolution order: project → user → marketplace.
- Enforcement: deterministic `mustPass` checks (`fileExists`, `fileMatches`, `commandSucceeds`, `stepSummaryMatches`).
- AI cross-checks (e.g., `check-doc-alignment`) are advisory, not blocking, in v0.1.

### Commits

Conventional Commits. The `polymath-release` plugin enforces this for release-style work.

### License

Apache-2.0 for all plugins. Patent grant matters for OSS plugins reused in commercial agents.

## Output

When loaded, this skill returns a one-paragraph summary appropriate to the current task, plus pointers to the relevant subsection above.
