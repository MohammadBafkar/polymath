---
prompt: "Here is the error: https://acme.sentry.io/issues/4509823/ — what happened?"
must_appear:
  - "polymath-observability:sentry-issue"
---
Sentry issue URL is a clean hard signal with no existing owner (PR/incident URLs
were already owned by reviewPR/respondToIncident; Sentry was the genuinely new one).
