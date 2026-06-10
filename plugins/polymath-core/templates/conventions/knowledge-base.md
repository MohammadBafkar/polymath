# {{org_or_project}} knowledge base

> **Canonical authority notice.** This document is a working derivation of
> the canonical sources listed below, kept in the repo because it is faster
> for agents to read than the source systems. On any conflict, the canonical
> source wins. Items marked `[VERIFY: …]` have not been confirmed against
> their source — do not treat them as authoritative until verified.

## Canonical sources

One row per system of record. "When to consult" tells an agent (or human)
which questions this source answers better than the derived docs.

| Source | URL | Owner | Update cadence | When to consult |
|--------|-----|-------|----------------|-----------------|
| {{source_name}} | {{url}} | {{owner}} | {{cadence}} | {{when_to_consult}} |

## Domain map

What each domain/bounded context owns, and the seams between them.

- **{{domain}}** — owns {{responsibility}}. Integrates with {{neighbors}} via {{seam}}. [VERIFY: confirm ownership with {{owner}}]

## How to use this knowledge base

- Working inside a domain → read its row in the domain map, then the
  relevant stack doc (see `conventions_docs` in `.polymath/project.yaml`).
- Making an architectural decision → check the canonical sources table for
  the system of record before relying on any derived doc.
- A derived doc contradicts its canonical source → fix the doc, note the
  source and date in the PR description, and escalate to the owner.

## Maintenance

| Doc | Maintainer | Review cadence |
|-----|------------|----------------|
| {{doc}} | {{maintainer}} | {{cadence}} |

Obsolete convention docs get a `[DEPRECATED: {{date}} — see {{url}}]` header
and stay in place; they are never silently deleted.
