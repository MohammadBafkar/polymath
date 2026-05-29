---
workflow: rootCauseAnalysis
scenario: rootCauseAnalysis-checkout-500s
expect:
  output_matches:
    - "docs/rca/.*-whys.md"
    - "docs/rca/.*-premortem.md"
    - "docs/rca/.*-challenge.md"
    - "([Cc]onfidence|[Uu]nknown|[Aa]ssumption)"
  timeout_seconds: 240
---

# Prompt

> Checkout started returning 500s under load this morning. Find the root cause.
>
> Run `/polymath-flows:run-workflow rootCauseAnalysis title="checkout 500s under load" symptom="POST /checkout returns 500 above ~200 rps, started after the 09:00 deploy"`.

# Acceptance

- 5-whys separates symptom from cause and stops at a system-level cause with cited evidence.
- The pre-mortem targets the PROPOSED fix, not the original system.
- The red-team produces at least one rival hypothesis and a distinguishing observation.
- The synthesis states a confidence label and whether the conclusion is gated on missing evidence.
- All output stays under `docs/rca/`.
