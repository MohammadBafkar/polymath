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
agent: optional-agent-name
disable_tools: false
effort: low
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

## How fixtures run

Both local and CI execution go through [`run-fixtures.sh`](run-fixtures.sh), which:

1. Spawns a scratch git repo per fixture.
2. Adds the local marketplace via `claude plugin marketplace add <repo>`.
3. Installs the plugin (or the full MVP set, for workflow fixtures).
4. Runs `claude -p "<prompt body>"` with the user's existing auth. Fixtures
   may declare `agent: <name>` to run an installed plugin agent directly,
   `disable_tools: true` for pure reasoning checks, and `effort: low|medium|high`
   when the fixture needs bounded model effort.
5. Checks `expect.invoked`, `expect.artifacts`, `expect.output_matches`, and `expect.not_invoked` against the transcript and scratch filesystem.

### Local

If you can already run `claude` from your shell, you can run fixtures:

```bash
tests/golden/run-fixtures.sh                                                # all
tests/golden/run-fixtures.sh tests/golden/polymath-core/plugin-budget-report.md  # one
tests/golden/run-fixtures.sh --plugin polymath-product                      # by plugin
```

No `ANTHROPIC_API_KEY` is required — the runner shells out to the Claude Code CLI you've already set up (Pro / Max / API key — any of them work).

### CI

The `claude-cli-fixtures` job in [`.github/workflows/golden-tests.yml.disabled`](../../.github/workflows/golden-tests.yml.disabled) installs the CLI, picks `CLAUDE_CODE_OAUTH_TOKEN` if present (subscription) or `ANTHROPIC_API_KEY` as a fallback, and calls the same `run-fixtures.sh`. If neither secret is set, the job emits a warning and skips the live run — fixture **parsing** still runs in `fixtures-parse`, catching frontmatter rot without spending tokens. **This workflow ships disabled** to avoid Claude API cost; rename it to `golden-tests.yml` to enable CI fixtures.

## Writing a fixture

- Keep the prompt under 200 words.
- Be explicit about the scenario in the title; "prd-from-rate-limit-request" is better than "scenario-1".
- Prefer fixtures that exercise one component end-to-end over fixtures that exercise many shallowly.
- Don't seed the scratch repo with code you also `expect:`; the fixture should produce the file.

## Bakeoffs

Golden fixtures prove component invocation. Bakeoffs prove outcome quality
against a baseline. See [`tests/bakeoff`](../bakeoff/) and run:

```bash
python3 tools/bakeoff.py check
python3 tools/bakeoff.py run
```
