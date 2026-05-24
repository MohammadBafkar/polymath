---
artifact: SunsetNotice
schemaVersion: 0.1
title: "{{title}}"
capability: "{{capability}}"
sunset_date: "{{sunset_date}}"
removal_date: "{{removal_date}}"
owner: "{{owner}}"
created: "{{date}}"
status: announced
---

# Sunsetting: {{capability}}

> A sunset notice has two dates the reader cares about: when the warning
> appears, and when the capability is removed. Anything else is filler.

## What's being sunset

`{{capability}}` — one-sentence description in the user's language. Not
internal name or system component; the thing the user knows it as.

## When

- **Today**: a deprecation warning appears. Use of `{{capability}}` still works.
- **{{sunset_date}}**: deprecation period begins. New usage is rejected; existing usage continues with a louder warning.
- **{{removal_date}}**: removal. Calls to `{{capability}}` return an error.

## Why

The motivation in one paragraph. User-impacting reason, not "tech debt". If
the reason is "we don't want to support it", say so plainly — readers respect
honesty.

## What you should do

The concrete migration. For most readers this is the only section that
matters.

```text
# Before
<old usage example>

# After
<new usage example>
```

If migration is non-trivial, link the migration guide.

## What replaces it

The supported alternative + a one-line comparison.

- **`{{replacement}}`** — does what `{{capability}}` did, but <difference>.

## Out of scope (not changing)

What you might be afraid is changing but isn't.

- …

## Exceptions / extensions

If certain customers need an extended window, the path to request it.

- Email <contact> by <date>.

## FAQ

- **Will my existing integrations break on {{sunset_date}}?** No — they continue to work, with a louder warning. Break is on **{{removal_date}}**.
- **Can I delay the removal?** Email <contact> with reasons by <date>.
- **What if I find a regression in the replacement?** Open an issue at <link>; we'll triage within <SLA>.

## References

- Migration guide: <link>
- Replacement documentation: <link>
- Original ADR / RFC for the change: <link>
