---
plugin: polymath-author
scenario: skill-author-critic-review
expect:
  invoked:
    - polymath-author:skill-author-critic
  output_matches:
    - "(Frontmatter|description)"
    - "(file:line|:[0-9])"
    - "(ACCEPT|REVISE|REWRITE)"
  not_invoked:
    - polymath-engineering:feature-dev
timeout_seconds: 90
---

# Prompt

> Review this SKILL.md.

Use polymath-author:skill-author-critic.

```markdown
---
name: brainstorm
description: This skill helps you brainstorm ideas by leveraging best practices to deliver outcomes that satisfy your needs and goals across a wide range of business and technical contexts.
---

# brainstorm

> Generate ideas.

## Procedure

1. Generate some ideas.
2. Pick the best one.
```

# Acceptance

- Verdict given: ACCEPT / REVISE / REWRITE.
- Each finding cites the relevant line in the SKILL.md.
- Description over 200 chars flagged.
- Missing "When to use" and "Output" and "Anti-patterns" sections flagged.
- "Procedure" steps flagged as not observable.
