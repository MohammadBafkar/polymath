# Skill-triggering tests

> Falsification anchor for skill `description:` quality.

Each `<plugin>/<skill>.md` file declares a naive user prompt that should
trigger the named skill, the must-invoke skill name, and (optionally) a
set of skills that may also be invoked. The runner at
[`tools/skill-triggering.py`](../../tools/skill-triggering.py) executes
each prompt via `claude -p --output-format stream-json`, parses tool
calls, and asserts the expected `Skill` tool-use happened.

The point is: a skill whose `description:` is too generic (vague trigger
phrase, hand-waving) will lose this test. The day a Polymath skill
silently goes "untriggerable" is the day this suite fails.

## File shape

```markdown
---
plugin: polymath-product
skill: prd
trigger_prompts:
  - "draft a PRD for rate-limiting /login"
  - "we need a product spec for the new refund flow"
must_invoke:
  - polymath-product:prd
allow_invoke:
  - polymath-thinking:*
---
```

Glob patterns are supported in `must_invoke` and `allow_invoke`. Any
invoke not matched by `must_invoke` ∪ `allow_invoke` is treated as a
*forbidden* invocation that fails the test.

## Runner

```bash
tools/skill-triggering.py check      # validate frontmatter (no LLM)
tools/skill-triggering.py list       # one row per test
tools/skill-triggering.py run        # opt-in: actually run claude
```

`run` is wired into `.github/workflows/evaluation.yml` and runs only
when secrets are present (skipped on fork PRs).
