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
2. The loader reads `.polymath/project.yaml` in the project → user (`${CLAUDE_CONFIG_DIR}/polymath/project.yaml`) → home order (first hit wins), then deep-merges the machine-local `./.polymath/project.local.yaml` overlay on top when one exists.
3. After validation against [`registry/schemas/project.schema.json`](../../../../registry/schemas/project.schema.json), the loader writes a resolved snapshot to `${CLAUDE_PLUGIN_DATA}/polymath-core/project-context.json` (plus a `_meta` block recording source path, overlay, ignored keys, and load time).
4. Skills read that JSON file directly.

## Procedure

To consume the context inside a skill. The data dir is namespaced per
plugin+marketplace when harness-managed, so resolve the snapshot by glob
(newest wins), never by a single hardcoded path:

```bash
ctx="$(ls -t "$HOME"/.claude/plugins/data/*/polymath-core/project-context.json \
            "$HOME"/.claude/plugins/data/polymath-core/project-context.json 2>/dev/null | head -1)"
if [[ -n "$ctx" ]]; then
  primary_lang="$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); s=d.get('stack',{}).get('languages',[]); print(s[0]['lang'] if s else '')" "$ctx")"
  # ...
fi
```

Inside a markdown skill (no shell), Read the same glob-resolved JSON file as the procedure's first step; if it is absent, skip silently and use built-in defaults.

### The consumption contract

A localizing skill applies, in this order, whichever of these exist in the snapshot:

1. **`conventions_docs` (by role)** — read the docs whose role keys are relevant to the skill and treat their Hard rules as guardrails. Conventional role names: `knowledge-base`, `backend-stack`, `frontend-stack`, `database`, `auth`, `deployment`, `shared-libraries`, `review-checklist`, `artifact-matrix`, `api-style` (keys are free-form; these are the names skills look for). Content marked `[VERIFY: …]` is inferred-not-confirmed — never treat it as authoritative, and surface relevant markers when they affect a decision.
2. **`skill_overrides["<plugin>:<skill>"]`** — `additional_context` files to read, `additional_axes` to apply, `test_commands` matched by the project's primary language.
3. **`prompts.<artifact>_template`** — use the project's template instead of the catalog default.
4. **`tracker`** — any skill that CREATES work items applies the project's destination (`organization`/`project`/`area_path`/`iteration`, `work_item_types` category map) and the 3-layer provenance marking: (1) `marking.title_prefix` prepended to the title, (2) `marking.tag` as a tag/label, (3) a traceability footer in the body (creating surface, date, link to the source artifact). After creating: **read the item back** and verify all three layers landed — re-apply whatever is missing. Items are pushed **HITL only**: present the full ticket set and get one explicit confirmation in-conversation before any create call; never push silently.

Wired consumers and their roles:

- **`polymath-engineering:code-review`** — roles `review-checklist` + the stack docs; plus `additional_context`/`additional_axes`; cite `conventions.code_review_checklist` in the review summary.
- **`polymath-engineering:verify-change`** — `test_commands` matching the primary language.
- **`polymath-engineering:feature-dev`** — roles `backend-stack`/`frontend-stack`/`shared-libraries`.
- **`polymath-backend:api-design-rest`** — roles `api-style`/`backend-stack`.
- **`polymath-backend:db-schema`** — role `database`.
- **`polymath-devops:dockerize`** — role `deployment`.
- **`polymath-devops:ci-pipeline-github`** — role `deployment`.
- **`polymath-release:pr`** — `prompts.pr_description_template`.
- **`polymath-incident:postmortem-blameless`** — `prompts.postmortem_template`.
- **`polymath-tracker:file-bug-from-incident` / `jira-triage` / `linear-triage`** — the `tracker` block (destination + 3-layer marking + readback + HITL push).

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
  "conventions_docs": { "backend-stack": "docs/conventions/backend-stack.md", ... },
  "smoke": { "dotnet": { "start": "...", "readiness": "/health" } },
  "routing": { "mode": "hint" },
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
