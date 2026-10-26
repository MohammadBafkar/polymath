---
name: migration-guide
description: Write a consumer migration guide for a breaking change — before/after examples, ordered steps, gotchas, rollback. Consumer upgrade steps, not the deprecation timeline (deprecation-plan).
---

# migration-guide

> A migration guide earns its keep when a consumer can follow it start to finish without asking a question. Show the diff, not the philosophy.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- You're deprecating or breaking something and consumers need concrete steps to move off it.
- The user asks for an upgrade/migration guide for an API/library/config change.
- A workflow invokes `polymath-release:migration-guide`.

This writes the *consumer upgrade steps*. It is not the deprecation timeline/policy (`polymath-release:deprecation-plan`), the customer-facing sunset notice (`polymath-communication:write-sunset-notice`), or a runtime/version migration of your own codebase (the `migrateLanguageVersion` workflow).

## Inputs

- The old and new way (API shape, config keys, behavior).
- Who is migrating (audience skill level) and the most common usage patterns. Unknown patterns: derive them from the old API's call sites or docs, and mark any guessed pattern `[VERIFY]`.
- Every before/after example must be checked against the real old and new APIs (read the code or docs); an example you could not verify is marked `[VERIFY: untested]`.

## Procedure

1. **State the change in one line** and whether it's mechanical or requires judgment.
2. **Before / after** — for each common pattern, show the old code and the new code side by side. Lead with the 80% case.
3. **Step order** — numbered, smallest safe steps; note which steps are reversible and where a checkpoint is safe.
4. **Gotchas** — behavioral differences, defaults that changed, things that look equivalent but aren't.
5. **Verify** — how the consumer confirms the migration worked (a test, an output, a log line).
6. **Rollback** — how to revert if something breaks mid-migration.
7. **Codemod** — if the change is mechanical at scale, provide or point to an automated codemod.
8. **Slug** from the change (e.g. `v1-search-to-v2`): a workflow's `${workflow.slug}` wins; otherwise lowercase it, replace each run of characters outside `a-z0-9` with `-`, trim `-` at the ends, and cut to ≤ 60 characters at a `-`. An existing file at the target path is updated in place (show the diff), never duplicated.
9. Write `docs/migrations/<slug>-guide.md`.

## Output

`docs/migrations/<slug>-guide.md`, in this shape:

````markdown
# Migrating from /v1/search to /v2/search

**Change:** results are paginated with a cursor instead of `page=` — mechanical for most callers.

## Before / after (most common first)

```diff
- GET /v1/search?q=refund&page=2
+ GET /v2/search?q=refund&cursor=<next_cursor from the previous response>
```

## Steps
1. Upgrade the SDK to ≥ 4.8 (reversible: pin back to 4.7).
2. Replace `page` loops with `next_cursor` loops — checkpoint: tests pass on 4.8.
3. Remove the v1 client config (irreversible once deployed; do it last).

## Gotchas
- `total_count` is no longer returned; it is expensive at scale — use `has_more`.

## Verify
Run `sdk-doctor search` — it prints `v2 OK`.

## Rollback
Steps 1–2 revert by pinning the SDK to 4.7; step 3 needs the v1 config restored before 2027-02-01.
````

## Quality bar

- Every common usage pattern has a concrete before/after, not prose.
- Steps are ordered and each is independently verifiable; the happy path is followable without external help.
- Behavioral gotchas (not just API renames) are called out.
- A rollback is given for any step that isn't trivially reversible.
