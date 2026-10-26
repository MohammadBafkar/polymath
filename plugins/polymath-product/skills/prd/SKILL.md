---
name: prd
description: Draft a PRD from a problem statement plus user/context inputs; populates docs/prds/<slug>.md from the canonical PRD template.
---

# prd

> Draft a Product Requirements Document. The output is a single Markdown file at `docs/prds/<slug>.md` that fills in the Polymath PRD template.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- The user says "draft a PRD", "write a spec", or "we need requirements for X".
- A workflow step invokes `polymath-product:prd`.
- A new feature needs explicit problem framing before implementation.

## Inputs

- Title (required) — short headline for the feature.
- Scope (optional, default `small`) — `small` or `medium`.
- Problem statement (required) — one-paragraph description from the user. Missing: ask; never draft a PRD around an invented problem.
- Users / context (optional) — known personas, existing PRDs, ADRs.

## Procedure

1. Read [`PRD.md`](../../templates/PRD.md).
2. **Slug** from the title: a workflow's `${workflow.slug}` wins; otherwise lowercase it, replace each run of characters outside `a-z0-9` with `-`, trim `-` at the ends, and cut to ≤ 60 characters at a `-`. An existing file at the target path is updated in place (show the diff), never duplicated.
3. **Summary-first checkpoint.** Before writing the document, show a
   one-screen skeleton — problem in one sentence, primary user, the three
   goals, any locked decisions — and confirm direction before the full
   draft.
   Unattended run (workflow step, subagent): nobody can confirm — skip the
   wait, write the document, and open the summary with the skeleton.
4. Create `docs/prds/<slug>.md` if it does not exist; otherwise update in place after surfacing the diff.
5. Fill each section:
   - **Problem** — restate the user's pain in their words first, then in product terms.
   - **Users / customers** — name the primary user type plus secondary if known.
   - **Goals** — three or fewer; each testable.
   - **Locked decisions** — decisions already made (discovery/ADR/owner,
     with source) the spec must not relitigate.
   - **Non-goals** — at least one; prevents scope creep.
   - **Deferral registry** — wanted-but-deferred scope, each entry with
     the condition that reopens it.
   - **Requirements** — enumerated, testable behaviors.
   - **Acceptance criteria** — Given / When / Then statements that map to test cases.
   - **Metrics** — adoption, quality, performance. Reference North Star if known. Baselines and targets come from data the user supplied; otherwise write `[TBD: baseline from <source>]` — never an invented number.
   - **Risks and open questions** — at least one open question if uncertainty exists.
   - **Out of scope** — explicit future work list.
   - **Rollout plan** — single paragraph; reference feature flags if applicable.
   - **References** — link related ADRs, RFCs, prior conversations.
6. After writing, surface a one-paragraph summary plus the file path.

## Quality bar

- No implementation language in **Goals** or **Requirements**.
- Each acceptance criterion is independently testable.
- At least one non-goal listed.
- At least one open question or risk listed.

## Output

- File: `docs/prds/<slug>.md`.
- Summary written to the workflow step summary (when invoked via `polymath-flows`).
