---
prompt: "let us improve the infra change process around here"
overlay: '{"rules": [{"id": "acmeInfra", "surface": "acme:infra-change", "intents": ["improve the infra change process"], "repo_state": ["*.tf"]}]}'
evidence: '{"*.tf": true}'
expect_silent: true
---
Precision invariant: repo evidence is a SOFT signal. Intent (1) + repo
boost (1) = 2 stays under the threshold of 3, and neither category is a
hard signal — soft-only combinations must never produce a hint, however
much repo context agrees with the phrasing.
