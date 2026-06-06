---
prompt: "Can you review this PR https://github.com/acme/web/pull/421 for correctness, security, and missing tests?"
must_appear:
  - "polymath-flows:run-workflow reviewPR"
  - "URL"
  - "alternative: polymath-engineering:code-review"
---
A PR URL plus a multi-concern "review" ask is the canonical reviewPR signal.
The hard signal (URL) is what licenses the hint; the intent phrasing only ranks it.
