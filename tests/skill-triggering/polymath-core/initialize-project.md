---
plugin: polymath-core
skill: initialize-project
trigger_prompts:
  - "I just installed Polymath in this repo. Set up the project context and tell future agents what tools and env vars they need."
  - "Create the .polymath config for this project from the README, AGENTS instructions, docs, and CI files."
  - "Make this repository ready for Polymath workflows with capabilities and onboarding notes."
must_invoke:
  - polymath-core:initialize-project
allow_invoke:
  - polymath-core:*
  - polymath-flows:*
---

# Why this test exists

Project activation prompts rarely mention the skill name. They ask for
setup, context, capabilities, onboarding, and agent readiness. The
initializer should trigger for all of those.
