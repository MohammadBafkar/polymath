---
name: assertion-quality
description: Review test assertions — assert behavior not implementation; kill snapshot/tautological checks; one reason-to-fail per test; improves existing tests, not authoring them (unit-tests).
---

# assertion-quality

> A test is only worth its assertions. Make each one assert the behavior that matters, fail for one clear reason, and resist incidental change.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- A test passes but you doubt it would catch the bug it claims to.
- Reviewing assertions specifically — snapshot sprawl, asserting on logs, `assertTrue(true)`-style tautologies.
- A workflow invokes `polymath-qa:assertion-quality`.

This sharpens *assertions* in existing tests. It is not authoring tests (`polymath-qa:unit-tests`), broad smell review (`polymath-qa:test-smell`), or coverage gaps (`polymath-qa:coverage-gap`).

## Inputs

- The test(s) whose assertions to review.
- The behavior each test is meant to protect (from the test name or the spec).

## Anti-patterns to fix

- **Implementation assertions** — asserting internal calls/structure instead of observable behavior.
- **Over-broad snapshots** — whole-object/whole-string snapshots that break on any change and teach nothing.
- **Tautological / vacuous** — assertions that can't fail, or that re-assert the setup.
- **Missing negative space** — only the happy value checked; error/boundary/empty cases unasserted.
- **Multi-reason failures** — one test that can fail for several unrelated reasons.

## Procedure

1. For each test, state the one behavior it should protect.
2. Flag assertions that are implementation-coupled, over-broad, or vacuous; show the line.
3. Rewrite each to assert the behavior precisely — narrowest assertion that still fails when the behavior breaks.
4. Add the missing negative-space assertion (error/boundary) where the behavior implies one.
5. Ensure one clear reason-to-fail per test; split if not.

## Output

One block per reviewed test, worst first (vacuous > implementation-coupled > over-broad > missing negative space > multi-reason):

```text
Assertion review: tests/test_refunds.py — 4 tests, 3 findings

test_refund_created                       VACUOUS
  line 41: assert response is not None
  protects: a refund for a valid order returns 201 with the refund id
  rewrite:  assert response.status_code == 201
            assert response.json()["refund_id"] == expected_id

test_refund_calls_ledger                  IMPLEMENTATION-COUPLED
  line 58: mock_ledger.post.assert_called_once()
  protects: the order balance drops by the refund amount
  rewrite:  assert get_balance(order) == original - 25_00

test_refund_rejects_overdraw              MISSING NEGATIVE SPACE
  add:      assert refund(order, amount=balance + 1).status_code == 409

Unchanged (already behavior-precise): test_refund_idempotency_key
```

## Quality bar

- Each assertion maps to an observable behavior, not an internal detail.
- No whole-object snapshot stands in for a specific expected value.
- Every reviewed test would fail if its protected behavior regressed (and only then).
