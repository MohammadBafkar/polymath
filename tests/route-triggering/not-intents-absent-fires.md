---
prompt: "ACME-4711 is ready — ship the deploy to staging."
overlay: '{"rules": [{"id": "acmeDeploy", "surface": "acme:deploy-service", "regex": ["\\bACME-\\d+\\b"], "not_intents": ["postmortem", "roll back"]}]}'
must_appear:
  - "acme:deploy-service"
---
Counter-fixture for not-intents-veto: the same overlay rule with no veto
phrase in the prompt must fire on its hard regex signal. Without this,
the veto fixture could pass vacuously (a broken overlay also yields
silence).
