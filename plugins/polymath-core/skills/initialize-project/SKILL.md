---
name: initialize-project
description: Inspect a repository and create .polymath/project.yaml, capability mapping, and onboarding notes for Polymath-aware agents.
---

# initialize-project

> Turn an existing repo into a Polymath-localized project: context, setup expectations, capability providers, recommended plugins, and first-run guidance.

## When to use

- A user just installed Polymath and asks what to do first.
- A repo lacks `.polymath/project.yaml` or `.polymath/capabilities.yaml`.
- A team wants coding agents to know required tools, env vars, test commands, conventions, and recommended plugins.

## Preflight

Before inferring anything, run `polymath-core:doctor` (or
`bash ${CLAUDE_PLUGIN_ROOT}/skills/doctor/scripts/doctor.sh`). If a **required**
tool is missing, stop and relay the fix — the inference and validation steps
below need `python3`. The doctor also reports whether a `.polymath/project.yaml`
already exists, so you know up front whether this is a create or an update.

## Procedure

1. **Inventory the repo.** Read the most relevant local sources first:
   - `AGENTS.md`, `CLAUDE.md`, `README.md`, `CONTRIBUTING.md`.
   - `docs/**/*.md` that mention setup, architecture, testing, release, deployment, security, or operations.
   - CI files under `.github/workflows/`, package manifests, lock files, Docker/Kubernetes/Terraform files, and language build files.
2. **Infer conservatively.**
   - Stack: languages, frameworks, tests, build tools, runtime, database, package manager.
   - Conventions: commit style, branch strategy, review checklist, style guides, prompt templates.
   - Setup: context sources, required tools, first steps, and environment variable names.
   - Capabilities: issue tracker, VCS, CI, observability, pager, incident comms, cloud, runtime, vulnerability scanner.
   - Polymath usage: recommended plugins, workflows, and compatible agent surfaces.
3. **Search for environment names, never values.** Use patterns such as `API_KEY`, `TOKEN`, `SECRET`, `PASSWORD`, `DSN`, `DATABASE_URL`, `WEBHOOK`, and `OAUTH`. Record only variable names and purposes. Never write secret values.
4. **Write or update `.polymath/project.yaml`.**
   - Preserve existing user intent where present.
   - Add `setup:` and `polymath:` sections when inferred.
   - Prefer explicit `skill_overrides` for test commands and project-owned templates.
5. **Write `.polymath/capabilities.yaml` only for confident provider mappings.**
   - Example: GitHub remote plus GitHub Actions means `vcs: github` and `ci: github_actions`.
   - If a provider is unknown, omit it and list the question in the onboarding doc instead of guessing.
6. **Write `docs/polymath-onboarding.md`** for *this* project — never copy
   Polymath's own maintainer commands (`tools/validate-all.sh`, `bakeoff.py`,
   unittest discovery) into it; those exist only in the marketplace repo.
   Include:
   - First steps: `/polymath-core:doctor` to preflight, then how to run setup.
   - Required vs optional tools with check commands. Classify honestly:
     `bash` and `python3` are required; `git` and the `claude` CLI are
     recommended; PyYAML and `jq` are optional (do not mark `jq` required).
   - Environment variables / keys needed, names only, with owner or source if known.
   - The recommended plugin install set for this project and one line of *why* per plugin.
   - Useful workflows and when to run them.
   - Agent compatibility: skills port via agentskills.io; commands, hooks,
     workflows, and MCP are Claude Code surfaces. Note that on another agent the
     setup commands above do not run — export skills and hand-write `project.yaml`.
7. **Validate.**
   - Run `python3 plugins/polymath-core/hooks/scripts/load-project-context.py` from the repo root with a temp `CLAUDE_PLUGIN_DATA` when available.
   - Run project validation commands discovered from the repo only if they are cheap and safe.
   - Report assumptions, unknowns, and follow-up questions.

## Output

- `.polymath/project.yaml`.
- `.polymath/capabilities.yaml` when provider mappings are known.
- `docs/polymath-onboarding.md`.
- A short summary of inferred stack, required setup, recommended plugins, and unresolved questions.

## Quality bar

- No invented providers, tools, or secret values.
- The generated project file validates with the SessionStart loader.
- The onboarding doc is actionable for a new contributor in under five minutes.
- Existing project files are preserved unless the user explicitly asks for replacement.
