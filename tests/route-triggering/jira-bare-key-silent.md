---
prompt: "Take a look at PROJ-123 when you get a chance."
expect_silent: true
---
A bare project key with no Atlassian browse URL and no "jira" context is
genuinely ambiguous (Jira? Linear? an acronym?), so the deterministic hook stays
silent rather than guess. Locks the post-review precision fix.
