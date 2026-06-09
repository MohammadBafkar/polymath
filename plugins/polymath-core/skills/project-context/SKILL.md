---
name: project-context
description: Read .polymath/project.yaml — language, framework, conventions, external skills, skill overrides — so a skill can adapt to this project instead of giving generic guidance.
---

# project-context

> Expose the resolved `.polymath/project.yaml` snapshot to any Polymath skill that wants to localize itself to *this* project — language, testing tools, runtime, conventions, external skill catalogs, per-skill overrides.

## When to use

- A skill is about to produce generic guidance (a code-review checklist, a test command, a PR template) and there might be a project-specific override the project owner has declared.
- A workflow step needs to call a language-specific command but the workflow itself is language-agnostic.
- An agent needs to surface a one-paragraph project summary to the user (onboarding, status updates, "what am I looking at?").
- A skill needs setup expectations: required tools, environment variable names, recommended Polymath plugins, or agent compatibility.

## How it works

1. The polymath-core SessionStart hook runs `hooks/scripts/load-project-context.py` at every session start.
2. The loader reads `.polymath/project.yaml` in the project → user (`${CLAUDE_CONFIG_DIR}/polymath/project.yaml`) → home order. First hit wins.
3. After validation against [`registry/schemas/project.schema.json`](../../../../registry/schemas/project.schema.json), the loader writes a resolved snapshot to `${CLAUDE_PLUGIN_DATA}/polymath-core/project-context.json` (plus a `_meta` block recording source path + load time).
4. Skills read that JSON file directly.

## Procedure

To consume the context inside a skill:

```bash
ctx="${CLAUDE_PLUGIN_DATA:-$HOME/.claude/plugins/data}/polymath-core/project-context.json"
if [[ -f "$ctx" ]]; then
  primary_lang="$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); s=d.get('stack',{}).get('languages',[]); print(s[0]['lang'] if s else '')" "$ctx")"
  # ...
fi
```

Inside a markdown skill (no shell), use the same JSON file path and read it as the procedure's first step. Examples:

- **`polymath-engineering:code-review`** — apply additional context files declared under `skill_overrides["polymath-engineering:code-review"].additional_context`. Run additional review axes from `additional_axes`. Cite the project's `conventions.code_review_checklist` file in the review summary.
- **`polymath-engineering:verify-change`** — pick the test command from `skill_overrides["polymath-engineering:verify-change"].test_commands` matching the project's primary language.
- **`polymath-release:pr`** — when `prompts.pr_description_template` is set, use that as the template instead of the catalog default.
- **`polymath-incident:postmortem-blameless`** — when `prompts.postmortem_template` is set, use that.

## What's in the snapshot

The file mirrors `.polymath/project.yaml` with the original keys preserved plus a `_meta` block:

```json
{
  "schemaVersion": 1,
  "project": { "name": "refund-service", "description": "..." },
  "stack": { "languages": [{ "lang": "dotnet", "version": "8", "framework": "aspnet-core" }], ... },
  "conventions": { "commit_style": "conventional-commits", ... },
  "external_skills": [{ "source": "github.com/dotnet/skills", ... }],
  "capabilities": { "inherit_from": ".polymath/capabilities.yaml" },
  "setup": { "required_tools": [...], "environment": [...], "first_steps": [...] },
  "polymath": { "recommended_plugins": [...], "recommended_workflows": [...] },
  "skill_overrides": { "polymath-engineering:code-review": { ... } },
  "prompts": { "pr_description_template": "docs/pr-template.md" },
  "mcp_servers": { "vcs": "@azure-devops/mcp-server" },
  "_meta": { "source": "...", "loaded_at": "...", "schemaVersion": 1 }
}
```

If no project file exists, the snapshot is absent and skills fall back to their built-in defaults.

## What this skill does *not* do

- It does not validate the project file (the loader does that).
- It does not write to the snapshot — that's the loader's job.
- It does not pick external skill packages on the user's behalf — the SessionStart hook surfaces the recommendation; the user installs.

## Related

- [`registry/schemas/project.schema.json`](../../../../registry/schemas/project.schema.json) — schema.
- [`docs/PROJECT-LOCALIZATION.md`](../../../../docs/PROJECT-LOCALIZATION.md) — full reference.
- [`docs/CAPABILITIES.md`](../../../../docs/CAPABILITIES.md) — capability mapping (sibling file).
- [`polymath-core:initialize-project`](../initialize-project/SKILL.md) — creates the first project context package.
