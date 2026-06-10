# {{area}} conventions — {{org_or_project}}

> **Canonical authority notice.** Working derivation of {{canonical_source}};
> the source wins on conflict. `[VERIFY: …]` items are inferred (e.g. from
> code scanning), not confirmed — do not treat them as authoritative.

## Architecture directive

The TARGET for new work, stated imperatively, and what is LEGACY:

- **Target:** {{target_pattern}} (e.g. "modular monolith on {{framework}}").
- **Legacy:** {{legacy_pattern}} — reference material only; do not extend.
  [VERIFY: confirm the legacy boundary with the owning team]

## Detected stack

Per repo/module. "Detected" = found by scanning; "Recommended" = the team's
stated choice. Where they differ, a `[VERIFY: …]` marker bridges the gap.

| Component | Version | Detected/Recommended | Notes |
|-----------|---------|----------------------|-------|
| {{component}} | {{version}} | {{status}} | {{notes}} |

## Hard rules

Non-negotiable. Skills treat these like guardrails, not suggestions.

- **Rule:** {{rule}} (why: {{reason}})
- **Never:** {{anti_pattern}}

## Project structure

```text
{{structure_tree_with_per_directory_purpose}}
```

## Recommended starting stack

For NEW services/components in this area:

| Decision | Recommendation | Rationale |
|----------|----------------|-----------|
| {{decision}} | {{recommendation}} | {{rationale}} |

## Open questions

`[VERIFY: …]` items collected for the team to confirm:

1. [VERIFY: {{question}}]
