---
prompt: "Deploy the acme stack to staging for ACME-1234, the release train is ready."
overlay: '{"rules": [{"id": "acmeDeploy", "kind": "skill", "surface": "acme:deploy-runbook", "trust": "auto-headless", "regex": ["\\bACME-\\d+\\b"], "intents": ["deploy the acme stack"]}]}'
must_appear:
  - "acme:deploy-runbook"
  - "project overlay"
must_not_appear:
  - "auto-headless"
---
A project routing overlay (`.polymath/route-signals.project.json`) adds a
company-specific rule: a hard regex signal (ACME ticket key) plus an intent
phrase. The hook must surface the overlay rule and label it as coming from
the project overlay — and must STRIP the rule's `trust: auto-headless`
claim (a project file can never claim an elevated trust axis, so the trust
line must not be printed even though this rule is the top candidate).
SURFACE-2 never sees this rule — overlays are resolved at scoring time,
marketplace uniqueness stays build-time-internal.
