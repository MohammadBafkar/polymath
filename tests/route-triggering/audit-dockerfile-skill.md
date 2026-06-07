---
prompt: "Audit the Dockerfile for security and best practices."
must_appear:
  - "polymath-devops:audit-dockerfile"
---
Disambiguation: audit-dockerfile and dockerize share the Dockerfile path, so both
appear as candidates — but the intent ("audit the dockerfile") makes audit-dockerfile
the top-scored (3 vs 2) primary. The sibling dockerize-skill fixture proves the tie
breaks the other way for "write a Dockerfile". (The hook lists up to 3 ranked
candidates, so the lower-scored sibling is expected to appear too.)
