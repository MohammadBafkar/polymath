---
prompt: "Check this Linear ticket https://linear.app/acme/issue/ENG-42 please."
must_appear:
  - "polymath-tracker:linear"
must_not_appear:
  - "polymath-tracker:jira"
---
A linear.app issue URL routes to the linear tool. jira must NOT appear: jira's
hard signal is the Atlassian browse URL only (its over-broad bare-key regex was
removed), so a Linear key inside a linear.app URL no longer misroutes to Jira.
