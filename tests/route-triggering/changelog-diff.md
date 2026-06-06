---
prompt: |
  Add a changelog entry for this:
  diff --git a/src/auth.ts b/src/auth.ts
  @@ -10,6 +10,7 @@
  +  rateLimit(login);
must_appear:
  - "polymath-release:changelog"
---
Inline diff is a hard signal; combined with the changelog intent it routes to the
changelog skill. Guards the DIFF_RE detector.
