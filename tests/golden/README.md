# Golden fixtures

> Spec-style fixtures that describe expected Polymath plugin behavior. Each fixture is a Markdown file with a YAML frontmatter block plus a body of prose. CI runs `claude -p` against each fixture and checks that the named component(s) were invoked.

## Layout

```text
tests/golden/
├── README.md                                # this file
├── <plugin>/
│   └── <scenario>.md
└── workflows/
    └── <workflow>.md
```

## Fixture format

```markdown
---
plugin: polymath-product
scenario: prd-from-rate-limit-request
expect:
  invoked:
    - polymath-product:prd
  artifacts:
    - "docs/prds/rate-limit-login.md"
  not_invoked:
    - polymath-engineering:feature-dev
timeout_seconds: 120
---

# Prompt

> The user prompt that should trigger the expected behavior.

We need a PRD for rate-limiting the /login endpoint. Five attempts
per minute, then a 15-minute cool-down. Audience is the platform
team.

# Acceptance

Bullet list of what a successful run produces. Used by reviewers; CI
checks the structured `expect:` block above.

- A docs/prds/rate-limit-login.md file with PRD frontmatter.
- The PRD includes Problem, Users, Goals, Acceptance criteria.
- The Acceptance criteria mention at least one negative path.
```

## How CI uses fixtures

1. Each fixture runs `claude -p "<prompt body>"` in a scratch repo seeded with the marketplace symlink.
2. The transcript is grepped for `invoked` capability labels (skill/command names).
3. The scratch filesystem is checked against `expect.artifacts`.
4. CI fails if any expected invocation is missing or any expected artifact is absent.

If `ANTHROPIC_API_KEY` is not configured in CI, fixtures are
**collected and parsed** (catches frontmatter rot) but not executed.

## Writing a fixture

- Keep the prompt under 200 words.
- Be explicit about the scenario in the title; "prd-from-rate-limit-request" is better than "scenario-1".
- Prefer fixtures that exercise one component end-to-end over fixtures that exercise many shallowly.
- Don't seed the scratch repo with code you also `expect:`; the fixture should produce the file.
