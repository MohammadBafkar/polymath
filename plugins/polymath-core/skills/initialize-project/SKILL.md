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

**Org packs.** Check the available-skills list for a skill named
`<anything>:org-defaults` — that is the convention for an installed
organization pack that ships starter `.polymath/` config and a conventions
corpus. If one is present and the repo has no `.polymath/project.yaml` yet,
propose running it FIRST (it copies the org's defaults in), then run this
skill to refine on top — inference must preserve the copied org intent the
same way it preserves user intent.

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
   - Map existing convention docs into `conventions_docs` by role
     (`review-checklist`, `backend-stack`, `database`, `deployment`, … —
     the vocabulary is in `polymath-core:project-context`). A file already
     referenced by `conventions.code_review_checklist` doubles as the
     `review-checklist` role.
5. **Offer to scaffold `.polymath/conventions/`** (skip silently if the
   user declines or docs already exist). Start from the skeletons in
   `${CLAUDE_PLUGIN_ROOT}/templates/conventions/` — minimum viable is one
   `stack-doc` per detected primary area plus `review-checklist`;
   `knowledge-base` and `artifact-matrix` are offered, not pushed. Fill
   placeholders only from what inference actually established; every
   inferred-not-confirmed claim carries an inline `[VERIFY: <question>]`
   marker, and unfillable placeholders stay as explicit gaps rather than
   invented content. Register every scaffolded doc in `conventions_docs`.
6. **Write `.polymath/capabilities.yaml` only for confident provider mappings.**
   - Example: GitHub remote plus GitHub Actions means `vcs: github` and `ci: github_actions`.
   - If a provider is unknown, omit it and list the question in the onboarding doc instead of guessing.
7. **Write `docs/POLYMATH-ONBOARDING.md`** for *this* project — never copy
   Polymath's own maintainer commands (`tools/validate-all.sh`, `bakeoff.py`,
   unittest discovery) into it; those exist only in the marketplace repo.
   Include:
   - First steps: `/polymath-core:doctor` to preflight, then how to run setup.
   - Required vs optional tools with check commands. Classify honestly:
     `bash` and `python3` are required; `git` and the `claude` CLI are
     recommended; PyYAML and `jq` are optional (do not mark `jq` required).
   - Environment variables / keys needed, names only, with owner or source if known.
   - The recommended plugin install set for this project. **Start from the
     closest install profile** in [`registry/polymath-profiles.json`](../../../../registry/polymath-profiles.json)
     (`backend`, `frontend`, `sre`, `platform`, `pm`, `staff`, `author`) — pick
     the one whose spine matches the inferred stack/role, emit its
     `claude plugin install` line verbatim (every profile already includes the
     `polymath-core` + `polymath-flows` spine), then add project-specific extras
     a-la-carte with one line of *why* per added plugin. Naming a profile turns
     "which of ~40 plugins?" into one decision plus a short delta.
   - Useful workflows and when to run them.
   - Agent compatibility: skills port via agentskills.io; commands, hooks,
     workflows, and MCP are Claude Code surfaces. Note that on another agent the
     setup commands above do not run — export skills and hand-write `project.yaml`.
8. **Validate.**
   - Run `python3 plugins/polymath-core/hooks/scripts/load-project-context.py` from the repo root with a temp `CLAUDE_PLUGIN_DATA` when available.
   - Run project validation commands discovered from the repo only if they are cheap and safe.
   - Report assumptions, unknowns, and follow-up questions — including the
     count of open `[VERIFY: …]` markers in any scaffolded conventions.

## Output

- `.polymath/project.yaml` (with `conventions_docs` when docs exist or were scaffolded).
- `.polymath/conventions/` when the user accepted the scaffold offer.
- `.polymath/capabilities.yaml` when provider mappings are known.
- `docs/POLYMATH-ONBOARDING.md`.
- A short summary of inferred stack, required setup, recommended plugins, and unresolved questions.

## Quality bar

- No invented providers, tools, or secret values.
- The generated project file validates with the SessionStart loader.
- The onboarding doc is actionable for a new contributor in under five minutes.
- Existing project files are preserved unless the user explicitly asks for replacement.
