---
name: write-release-notes
description: Author customer-facing release notes — headline, user-benefit framing, breaking changes called out, no internal-jargon component names.
---

# write-release-notes

> Customer-facing release notes. Different from CHANGELOG: the audience is users, not engineers. Tone is announcement + benefit, not changelog rollup.

## When to use

- A release is being prepared and you want notes the customer-facing site / email blast can use.
- The internal CHANGELOG exists; this skill repackages it for users.

## Inputs

- The version being released + date.
- The CHANGELOG entries since the last release (or `git log --oneline`).
- Optional: any customer-reported issues that this release fixes (call out individually).

## Procedure

1. **Headline**: one sentence on the most important change. Lead with the benefit, not the mechanism.
2. **What's new**: each `Added` from the CHANGELOG, restated in customer language. Skip internal-only changes.
3. **Notable changes**: `Changed`, `Fixed`, `Security`, `Deprecated`, `Removed` that customers will notice.
4. **Breaking changes**: own section. Migration path required for each. If anyone has to change anything in their code or workflow, this section is mandatory.
5. **Known issues**: shipping ≠ no-bugs. Be honest about what's pending.
6. **Security fixes**: credit the reporter when they consented; cite the advisory ID.

## Style

- Active voice ("We added X" or "X now does Y").
- User benefit, not implementation ("Faster check-outs" beats "Optimized the cart query").
- No internal component names ("the checkout API" not "v2-cart-svc").
- No emojis.

## Output

```text
Release notes — Polymath v1.4.0 (2026-05-24)

Headline:
  Refunds now complete in under a second — a 4× speedup for high-volume merchants.

What's new
  - Refund creation is now sub-second at P95 across all regions.
  - You can now view refund status in the timeline view of an order.

Notable changes
  - Idempotency-Key is now required on refund retries (previously optional).
    See the migration note below.

Breaking changes
  - `POST /v1/refunds` now requires `Idempotency-Key` header on retries. Calls
    without it on a retry return 400.
    Migration: include a UUID `Idempotency-Key` per refund attempt.

Security fixes
  - SEC-2026-0042 (Medium): IDOR on /v1/orders/{id}/refunds — fixed in 1.4.0.
    Reported by <name>. See advisory link.

Known issues
  - The new timeline view doesn't yet render correctly on IE11. Tracked in #1234.
```

## Quality bar

- Headline names benefit, not mechanism.
- Breaking changes have a Migration line each.
- Internal jargon scrubbed; if the customer wouldn't recognize a component name, replace it.
- Active voice.
- Security fixes credit reporters who consented.

## Anti-patterns to avoid

- Pasting the CHANGELOG without rewriting for customer audience.
- "Performance improvements" without a number.
- Burying breaking changes in the middle of "Notable changes".
- Marketing puffery ("We're excited to announce …"). Just say what changed.
