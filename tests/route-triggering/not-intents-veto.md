---
prompt: "ACME-4711 is hot — but first write the postmortem for yesterday's deploy outage."
overlay: '{"rules": [{"id": "acmeDeploy", "surface": "acme:deploy-service", "regex": ["\\bACME-\\d+\\b"], "not_intents": ["postmortem", "roll back"]}]}'
expect_silent: true
---
A matching not_intent vetoes the surface even though its hard signal
(the ACME-#### ticket regex, score 3) fired: the prompt is about the
postmortem, not the deploy. The veto must remove the rule from scoring
entirely, leaving nothing above threshold.
