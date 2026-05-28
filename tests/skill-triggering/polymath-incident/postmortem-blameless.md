---
plugin: polymath-incident
skill: postmortem-blameless
trigger_prompts:
  - "write a blameless postmortem for yesterday's outage"
  - "draft the retro for the refund-async incident — make sure it's not blame-shaped"
  - "I need a postmortem that names systemic causes, not people"
must_invoke:
  - polymath-incident:postmortem-blameless
allow_invoke:
  - polymath-thinking:5-whys
  - polymath-thinking:*
  - polymath-core:*
---

# Why this test exists

"Postmortem" is the canonical trigger. The third prompt deliberately
avoids the word "postmortem" to catch over-fitting; "names systemic
causes, not people" is the blameless-postmortem domain in the user's
language.
