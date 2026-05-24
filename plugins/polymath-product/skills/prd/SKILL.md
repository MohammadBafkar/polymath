---
name: prd
description: Draft a PRD from a problem statement plus user/context inputs; populates docs/prds/<slug>.md from the canonical PRD template.
---

# prd

> Draft a Product Requirements Document. The output is a single Markdown file at `docs/prds/<slug>.md` that fills in the Polymath PRD template.

## When to use

- The user says "draft a PRD", "write a spec", or "we need requirements for X".
- A workflow step invokes `polymath-product:prd`.
- A new feature needs explicit problem framing before implementation.

## Inputs

- Title (required) — short headline for the feature.
- Scope (optional, default `small`) — `small` or `medium`.
- Problem statement (required) — one-paragraph description from the user.
- Users / context (optional) — known personas, existing PRDs, ADRs.

## Procedure

1. Read [`PRD.md`](../../templates/PRD.md).
2. Compute a slug from the title: lowercase, kebab-case, no special characters.
3. Create `docs/prds/<slug>.md` if it does not exist; otherwise update in place after surfacing the diff.
4. Fill each section:
   - **Problem** — restate the user's pain in their words first, then in product terms.
   - **Users / customers** — name the primary user type plus secondary if known.
   - **Goals** — three or fewer; each testable.
   - **Non-goals** — at least one; prevents scope creep.
   - **Requirements** — enumerated, testable behaviors.
   - **Acceptance criteria** — Given / When / Then statements that map to test cases.
   - **Metrics** — adoption, quality, performance. Reference North Star if known.
   - **Risks and open questions** — at least one open question if uncertainty exists.
   - **Out of scope** — explicit future work list.
   - **Rollout plan** — single paragraph; reference feature flags if applicable.
   - **References** — link related ADRs, RFCs, prior conversations.
5. After writing, surface a one-paragraph summary plus the file path.

## Quality bar

- No implementation language in **Goals** or **Requirements**.
- Each acceptance criterion is independently testable.
- At least one non-goal listed.
- At least one open question or risk listed.

## Output

- File: `docs/prds/<slug>.md`.
- Summary written to the workflow step summary (when invoked via `polymath-flows`).
