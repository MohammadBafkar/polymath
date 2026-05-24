---
name: refund-or-dispute-triage
description: Classify a Stripe charge/refund/dispute and produce a triage plan + customer-comms-safe summary. Read-only by default; refunds require explicit operator approval.
---

# refund-or-dispute-triage

> Given a charge, refund, or dispute ID, gather the facts and propose a next action without sending PCI-sensitive data downstream. Output is a structured triage + a customer-safe summary.

## When to use

- Customer support escalates a charge dispute and engineering needs the system view.
- A `polymath-incident` post-action surfaces a payment regression and you need to know which charges are affected.
- A refund-policy review asks "did we actually refund the right charges last week?"

## Inputs

- Object ID (required) — Stripe ID with prefix (`ch_…`, `re_…`, `dp_…`, `pi_…`). Refuse short, prefix-stripped IDs.
- Mode (required) — `live` or `test`. Live mode requires explicit confirmation in the prompt context.

## Procedure

1. **Resolve the object kind** from the ID prefix. Refuse unknown prefixes.
2. **Fetch the object** read-only:
   - charge → `charges.retrieve` (expand `customer`, `payment_method`, `latest_charge`, `outcome`).
   - refund → `refunds.retrieve` (expand `charge`).
   - dispute → `disputes.retrieve` (expand `charge`, `evidence`).
   - payment_intent → `payment_intents.retrieve` (expand `latest_charge`).
3. **Read related events.** `events.list` with `object[id]=<id>` to recover the lifecycle: created → authorized → captured → refunded / disputed / etc.
4. **Classify the situation.**
   - **Legitimate refund needed** — customer claim is valid; recommend `refunds.create` (NOT executed automatically; surface as a proposed action with the exact API call).
   - **Friendly fraud / chargeback** — dispute filed despite a fulfilled purchase. Evidence packet needed (`disputes.update` with `evidence`).
   - **Duplicate charge** — multiple `pi_*` for the same intent. One legitimate, others to refund.
   - **System-failure refund** — refund already issued by automation; verify it landed (`refund.status = succeeded`).
   - **Out-of-scope** — operator should escalate to a human (large amount, repeat customer, regulatory).
5. **Customer-comms summary.** Produce a body the support agent can paste without revealing card details. Never include full PAN, BIN, or anti-fraud signals — Stripe filters these but the summary should be conservative even if the API returns them.
6. **Surface the proposed action as an explicit API call**, never as an executed mutation. The operator approves and runs it (or kicks off a separate workflow).

## Output

```text
refund-or-dispute-triage

Object:        ch_3OabCD (charge, live mode)
Customer:      cus_NXYZ (email redacted: a…@example.com)
Amount:        $42.00 USD
Captured:      2026-05-20 14:11 UTC
State:         disputed (dp_1OefGH, reason: "duplicate")
Lifecycle:
  - 2026-05-20 14:09  payment_intent.created
  - 2026-05-20 14:11  charge.succeeded
  - 2026-05-22 09:02  charge.dispute.created
  - 2026-05-22 09:02  charge.dispute.funds_withdrawn

Classification: duplicate-charge dispute
  Reason: an earlier successful charge (ch_3Oabaa) covered the same order_id
          ord_12345. Stripe API confirms; our order ledger agrees.

Proposed action (operator approval required):
  Submit evidence to dispute dp_1OefGH:
    - duplicate_charge_id      = ch_3Oabaa
    - duplicate_charge_documentation: order receipt URL
  API call:
    disputes.update(id='dp_1OefGH', evidence={
      duplicate_charge_id: 'ch_3Oabaa',
      duplicate_charge_documentation: '<file_id>'
    })

Customer-safe summary (for support agent):
  > We confirmed an earlier successful charge covered this order.
  > We are submitting that evidence to your bank. The card-issuer's
  > response typically takes 7-21 business days.
```

## Quality bar

- Object kind classified by ID prefix.
- Read-only fetches; no mutating API calls in the skill itself.
- Customer summary contains no PAN, BIN, or anti-fraud signal.
- Proposed action surfaced as an explicit API call for operator approval.

## Anti-patterns to avoid

- Executing `refunds.create` automatically. Refunds are money-moving operations; require a human in the loop.
- Logging full card numbers. The Stripe API redacts most but not all fields; treat the whole response as PCI-adjacent.
- Defaulting to `live` mode. Test mode is the safer default; live requires explicit operator confirmation.
- Trusting the dispute `reason` field alone. The reason is what the cardholder claimed; cross-check against your ledger.
