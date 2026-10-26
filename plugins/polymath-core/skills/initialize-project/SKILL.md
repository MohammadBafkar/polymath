---
name: initialize-project
description: Map a repository to .polymath/project.yaml — capability mapping and onboarding notes for Polymath-aware agents.
---

# initialize-project

> Turn an existing repo into a Polymath-localized project: context, setup expectations, capability providers, recommended plugins, and first-run guidance.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- A user just installed Polymath and asks what to do first.
- A repo lacks `.polymath/project.yaml` or `.polymath/capabilities.yaml`.
- A team wants coding agents to know required tools, env vars, test commands, conventions, and recommended plugins.

## Inputs

- The repository (required) — run from its root.
- Existing `.polymath/project.yaml`, `.polymath/capabilities.yaml`, `POLYMATH.md`
  (or a legacy `docs/POLYMATH-ONBOARDING.md`) — optional; when present this is
  an **update**, and user-written content wins over inference.
- Optional project name override (the `activateProject` workflow's `projectName`).
- Unattended runs (a workflow step, a subagent, `claude -p`): nobody answers
  offers. Skip every offer (conventions scaffold, defaults packs, pointer
  lines), list them under "Follow-ups" in the summary, and never guess a
  provider to avoid asking.

## Preflight

Before inferring anything, run `polymath-core:doctor` (or
`bash "${POLYMATH_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}/skills/doctor/scripts/doctor.sh"`). If a **required**
tool is missing, stop and relay the fix — the inference and validation steps
below need `python3`. The doctor also reports whether a `.polymath/project.yaml`
already exists, so you know up front whether this is a create or an update.

**Defaults packs.** Check the available-skills list for skills named
`<anything>:apply-defaults` — the convention for installed defaults packs
that ship starter `.polymath/` config and a conventions corpus at some
scope (organization, team, product line, project archetype). If any are
present and the repo has no `.polymath/project.yaml` yet, propose running
them FIRST — narrowest scope first (project archetype → team → org), since
apply-defaults never overwrites and broader packs should only fill gaps —
then run this skill to refine on top. Inference must preserve the copied
pack intent the same way it preserves user intent.

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
   - Declare the routing posture explicitly — strictness must be a
     written, reviewable line, never ambient. Default to:

     ```yaml
     routing:
       mode: classify
     ```

     and offer `enforce` (mutating tool calls gated until the request is
     classified) when the team wants the strict loop. `hint` is the
     zero-ceremony opt-out for repos that only want ambient route hints.
     Block form only (`routing:` then indented `mode:`); `classify` and
     `enforce` take effect only with the `polymath-pipeline` plugin
     installed — when it is missing, say so and include it in the
     recommended install set.
   - Prefer explicit `skill_overrides` for test commands and project-owned templates.
   - Map existing convention docs into `conventions_docs` by role
     (`review-checklist`, `backend-stack`, `database`, `deployment`, … —
     the vocabulary is in `polymath-core:project-context`). A file already
     referenced by `conventions.code_review_checklist` doubles as the
     `review-checklist` role.
5. **Offer to scaffold `.polymath/conventions/`** (skip silently if the
   user declines or docs already exist). Start from the skeletons in
   `${POLYMATH_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}/templates/conventions/` — minimum viable is one
   `stack-doc` per detected primary area plus `review-checklist`;
   `knowledge-base` and `artifact-matrix` are offered, not pushed. Fill
   placeholders only from what inference actually established; every
   inferred-not-confirmed claim carries an inline `[VERIFY: <question>]`
   marker, and unfillable placeholders stay as explicit gaps rather than
   invented content. Register every scaffolded doc in `conventions_docs`.
6. **Write `.polymath/capabilities.yaml` only for confident provider mappings.**
   - Example: GitHub remote plus GitHub Actions means `vcs: github` and `ci: github_actions`.
   - If a provider is unknown, omit it and list the question in `POLYMATH.md` instead of guessing.
7. **Write `POLYMATH.md` at the repository root** for *this* project — the
   file a contributor or agent opens first, next to `README.md`. Never copy
   Polymath's own maintainer commands (`tools/validate-all.sh`, `bakeoff.py`,
   unittest discovery) into it; those exist only in the marketplace repo.
   - **Legacy location.** If `docs/POLYMATH-ONBOARDING.md` exists from an
     earlier init, move it first (`git mv docs/POLYMATH-ONBOARDING.md POLYMATH.md`
     when tracked, a plain move otherwise), then update it — never leave both
     files. Say in the summary that it moved.
   - **Existing `POLYMATH.md`.** Update in place: keep sections a human wrote,
     refresh only the facts inference re-derived, and show the diff before saving.
   Include:
   - First steps: `/polymath-core:doctor` to preflight, then how to run setup.
   - Required vs optional tools with check commands. Classify honestly:
     `bash` and `python3` are required; `git` and the `claude` CLI are
     recommended; PyYAML and `jq` are optional (do not mark `jq` required).
   - Environment variables / keys needed, names only, with owner or source if known.
   - The recommended plugin install set for this project. **Start from the
     closest install profile** in [`references/polymath-profiles.json`](references/polymath-profiles.json)
     (`backend`, `frontend`, `sre`, `platform`, `pm`, `staff`, `author`) — pick
     the one whose spine matches the inferred stack/role, emit its
     `claude plugin install` line verbatim (every profile already includes the
     `polymath-core` + `polymath-flows` spine), then add project-specific extras
     a-la-carte with one line of *why* per added plugin. Naming a profile turns
     "which of ~40 plugins?" into one decision plus a short delta.
   - The declared routing posture: name the `routing.mode` that was
     written and what it does for this repo; for `classify`/`enforce`,
     list `polymath-pipeline` in the install set.
   - Useful workflows and when to run them.
   - Agent compatibility: skills port via agentskills.io; commands and subagents
     export as converted skills; hooks, workflows, and MCP export as support
     metadata that require target-host wiring. Note that on another agent the
     hook-driven setup above does not run automatically.
   - Open questions: every unknown provider, unconfirmed inference, and open
     `[VERIFY: …]` marker, each as a question a teammate can answer.
   Then **offer** (never do unasked) a one-line pointer in the project's
   `AGENTS.md` / `CLAUDE.md` — `See POLYMATH.md for Polymath setup.` — so
   agents that read those files find it.
8. **Validate.**
   - Run the SessionStart loader against the file you wrote, from the repo root, with a throwaway data dir so the real snapshot is untouched:
     `POLYMATH_DATA_DIR="$(mktemp -d)" python3 "${POLYMATH_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}/hooks/scripts/load-project-context.py"`.
     Exit 0 = valid; exit 2 prints the validation errors — fix them and re-run before reporting success.
   - Run project validation commands discovered from the repo only if they are cheap, read-only, and need no credentials.
   - Report assumptions, unknowns, and follow-up questions — including the
     count of open `[VERIFY: …]` markers in any scaffolded conventions.

## Output

- `.polymath/project.yaml` (with `conventions_docs` when docs exist or were scaffolded).
- `.polymath/conventions/` when the user accepted the scaffold offer.
- `.polymath/capabilities.yaml` when provider mappings are known.
- `POLYMATH.md` at the repository root.
- A summary in this shape:

```text
Initialized: <project name>  (create | update)
Wrote:       .polymath/project.yaml, POLYMATH.md[, .polymath/capabilities.yaml][, .polymath/conventions/…]
Moved:       docs/POLYMATH-ONBOARDING.md → POLYMATH.md   (only when a legacy file existed)
Stack:       <languages / frameworks / test runner — inferred>
Routing:     routing.mode = <hint | classify | enforce>
Profile:     <profile> + <extras>   → claude plugin install … (in POLYMATH.md)
Validated:   load-project-context.py exit 0
Open:        <n> questions, <m> [VERIFY] markers — listed in POLYMATH.md
Follow-ups:  <offers skipped in an unattended run, or "none">
```

## Quality bar

- No invented providers, tools, or secret values.
- The generated project file validates with the SessionStart loader.
- `POLYMATH.md` is actionable for a new contributor in under five minutes.
- Exactly one onboarding file exists afterwards: root `POLYMATH.md`, never also `docs/POLYMATH-ONBOARDING.md`.
- Existing project files are preserved unless the user explicitly asks for replacement.
