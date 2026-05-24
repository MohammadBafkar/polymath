---
workflow: bugTriage
scenario: bugTriage-login-redirect-loop
expect:
  invoked:
    - polymath-flows:run-workflow
    - polymath-thinking:5-whys
    - polymath-engineering:read-code
    - polymath-engineering:code-review
    - polymath-planning:work-breakdown
  artifacts:
    - "docs/bugs/login-redirect-loop-whys.md"
    - "docs/bugs/login-redirect-loop-orient.md"
    - "docs/bugs/login-redirect-loop-plan.md"
  state_must_pass:
    - whys-exists
    - orient-exists
    - plan-exists
    - whys-cites-evidence
    - plan-names-critical-path
timeout_seconds: 600
---

# Prompt

> Triage this bug.

/polymath-flows:run-workflow bugTriage title="Login redirect loop" severity=sev3

Some users hit an infinite redirect after submitting /login. Recent deploy
changed the session-cookie domain.

# Acceptance

- 5-whys cites evidence (log lines or session-cookie domain change) and lands
  on a system-level cause, not "Alice misconfigured".
- read-code map names the auth/session module + 2 alternative areas.
- code-review surfaces correctness findings from the cookie-domain diff, or
  documents why the diff doesn't apply.
- work-breakdown plan names the critical path.
