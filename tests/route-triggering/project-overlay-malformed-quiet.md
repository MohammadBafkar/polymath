---
prompt: "Review this PR https://github.com/acme/web/pull/42 for correctness."
overlay: 'this is not json {{{'
must_appear:
  - "polymath-flows:run-workflow reviewPR"
must_not_appear:
  - "project overlay"
---
A malformed project overlay must be ignored entirely: the bundled catalog
rules still fire (the PR-review URL is a hard signal) and nothing about the
broken overlay reaches the output. Project config must never break a turn.
