---
name: migration-guide
description: Write a consumer migration guide for a breaking change — before/after examples, ordered steps, gotchas, rollback. Consumer upgrade steps, not the deprecation timeline (deprecation-plan).
---

# migration-guide

> A migration guide earns its keep when a consumer can follow it start to finish without asking a question. Show the diff, not the philosophy.

## When to use

- You're deprecating or breaking something and consumers need concrete steps to move off it.
- The user asks for an upgrade/migration guide for an API/library/config change.
- A workflow invokes `polymath-release:migration-guide`.

This writes the *consumer upgrade steps*. It is not the deprecation timeline/policy (`polymath-release:deprecation-plan`), the customer-facing sunset notice (`polymath-communication:write-sunset-notice`), or a runtime/version migration of your own codebase (the `migrateLanguageVersion` workflow).

## Inputs

- The old and new way (API shape, config keys, behavior).
- Who is migrating (audience skill level) and the most common usage patterns.

## Procedure

1. **State the change in one line** and whether it's mechanical or requires judgment.
2. **Before / after** — for each common pattern, show the old code and the new code side by side. Lead with the 80% case.
3. **Step order** — numbered, smallest safe steps; note which steps are reversible and where a checkpoint is safe.
4. **Gotchas** — behavioral differences, defaults that changed, things that look equivalent but aren't.
5. **Verify** — how the consumer confirms the migration worked (a test, an output, a log line).
6. **Rollback** — how to revert if something breaks mid-migration.
7. **Codemod** — if the change is mechanical at scale, provide or point to an automated codemod.

## Quality bar

- Every common usage pattern has a concrete before/after, not prose.
- Steps are ordered and each is independently verifiable; the happy path is followable without external help.
- Behavioral gotchas (not just API renames) are called out.
- A rollback is given for any step that isn't trivially reversible.
