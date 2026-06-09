---
prompt: "Can you look at https://acme.atlassian.net/browse/PROJ-123 and summarize the bug?"
must_appear:
  - "polymath-tracker:jira"
---
Tool surface (Phase 3): the hard signal is the Atlassian browse URL (a bare key
is too ambiguous — see jira-bare-key-silent / acronyms-silent). The jira tool
replaces the old detect-ticket-key.sh bash detector via the unified registry.
