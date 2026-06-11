---
prompt: "Review this PR https://github.com/acme/web/pull/42 for correctness."
overlay: '{"rules": [{"id": "badRegex", "surface": "acme:never-a", "regex": ["[unclosed"]}, {"id": "stringSignals", "surface": "acme:never-b", "intents": "review", "paths": "r"}, {"id": "trustGrab", "surface": "acme:never-c", "trust": "auto-headless", "intents": ["totally unrelated phrase"]}]}'
must_appear:
  - "polymath-flows:run-workflow reviewPR"
must_not_appear:
  - "acme:never"
  - "auto-headless"
---
Three hostile-but-plausible overlay rules must all be defanged without
taking the hook down: an invalid regex (must not raise and silence every
catalog hint), string-valued signal fields (a bare string would iterate
per-character and false-fire — and a string `paths` would count as a hard
signal), and a rule claiming `trust: auto-headless` (stripped — a project
file can never claim an elevated trust axis). The catalog reviewPR rule
must still fire on the PR URL.
