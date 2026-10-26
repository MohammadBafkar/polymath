---
name: skill-author-critic
description: Review a SKILL.md against the style guide — frontmatter, procedure, output, anti-patterns; verdict ACCEPT/REVISE/REWRITE.
---

# skill-author-critic

> Critique one SKILL.md before it ships. Output is findings keyed to line numbers and a verdict.

## When to use

- A new skill is being added.
- An existing skill is being revised and the author wants a second look.
- A workflow's quality step needs a structured skill review.

## Inputs

- The path to a SKILL.md.

## Procedure

Walk the file top-to-bottom against the Polymath skill style guide
([`references/skill-style-guide.md`](../../references/skill-style-guide.md)):

1. **Frontmatter**:
   - `name`: kebab-case, matches the directory name.
   - `description`: ≤ 200 chars, leads with an imperative verb, says when the skill triggers — not what it does internally.
2. **Trigger phrase**: a one-line blockquote summarizing the skill's purpose in the user's voice. "Drives a TDD loop." — not "This skill is a TDD-loop driver."
3. **When to use**: 2–4 bullets describing concrete user phrases or workflow positions.
4. **Inputs**: required vs optional, with what defaults if absent.
5. **Procedure**: numbered steps. Each step is observable. No "consider X" — consider what, and what's the decision?
6. **Output**: a fenced code block showing the exact shape the skill produces. The model is going to imitate this; vague output sections produce vague outputs.
7. **Quality bar OR Anti-patterns** section (preferably both): pin failure modes the model would otherwise drift into.
8. **Body length**: ≤ 500 lines total. Anything longer should split into `references/*.md`.
9. **Routing posture declared (SURFACE-1)**: the skill either ships a `routing.yaml` sidecar (schema: `registry/schemas/surface-routing.schema.json`) or has a reasoned entry in `registry/routing-exemptions.json` — CI rejects a surface that is neither. Flag a missing choice, and flag `tier: hard` without a `tests/route-triggering/` fixture.

Then walk the **reliability lens** (the style guide's "Reliability contract") — structure passing is not enough; these are the defects that break real runs:

10. **Resolvable references**: every `plugin:skill` named exists; every link/path resolves *from an installed plugin* — no `plugins/<name>/…` or `tools/…` paths that exist only in the marketplace checkout; bundled scripts use `${POLYMATH_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}` (a bare `${POLYMATH_PLUGIN_ROOT}` is empty under Claude Code).
11. **Missing-input behavior**: says what happens when a required input, tool, or MCP server is absent (ask, assume-and-state, or stop) — never silently proceeds on a guess.
12. **Side-effect gates**: any outward-facing or hard-to-reverse action (post, publish, push, create ticket/monitor, run a generator, mutate infra/data) shows the exact action and waits for confirmation.
13. **Verification step**: the procedure proves its result (runs the test, reads back the created item, re-runs the plan) instead of asserting success; gates are satisfied honestly, never by echoing magic words.
14. **Fabrication guard**: numbers, names, owners, quotes, and dates come from inputs or are marked `[TBD]`/`[VERIFY]`; the quality bar does not pressure the model to invent them.
15. **Untrusted content**: text from issues, tickets, logs, web pages, or retrieved docs is treated as data, not instructions.
16. **Factual accuracy**: commands, flags, API names, standards versions, and arithmetic in the body and Output example are correct and current; examples obey the skill's own rules.
17. **Sibling consistency**: the description's scope boundary and the procedure agree with the sibling skills it names (no contradictory definitions, thresholds, or ownership).

For each finding, cite **file:line** and give the corrective change.

## Output

```text
skill-author-critic: plugins/polymath-foo/skills/bar/SKILL.md

Frontmatter:
  ✓ name matches directory.
  ✗ description: 217 chars (> 200). Trim "by leveraging the user's prior context to deliver" — that's filler.

Trigger phrase:
  ✓ present at line 6, imperative.

When to use:
  ✗ line 12: "When you want to use this skill" — meta-description. Replace with a concrete user phrase like "The user says 'review this'".

Procedure:
  ✗ line 28: "Consider whether to escalate" — consider HOW; what decides? Add the decision rule (e.g. "escalate when severity ≥ sev2").

Output:
  ✓ has a fenced code block at line 52.

Anti-patterns:
  ✗ section missing. Add 3 bullets covering the easy-mode failures.

Body length: 312 lines (under 500). ✓

Reliability:
  ✗ line 34: `python3 plugins/polymath-foo/bin/render.py` — marketplace-only path; breaks once installed.
    Use the plugin-root form from the style guide's Reliability contract.
  ✗ line 41: "Post the update to #incidents" — outward-facing with no confirmation. Show the message + channel and wait for approval.
  ✓ verification: step 7 reads the created item back.

Verdict: REVISE.
  Three structural + two reliability fixes above. Re-submit when frontmatter passes the 200-char gate, the Anti-patterns section exists, and the side effect is gated.
```

## Quality bar

- Every finding has file:line + a concrete corrective change.
- Verdicts: ACCEPT / REVISE / REWRITE. Not "looks good".
- No nitpicking unless it's a structural or reliability issue.
- A structurally perfect skill with an unresolvable path, an ungated side effect, or a factual error in its example is REVISE, not ACCEPT.

## Anti-patterns to avoid

- "Maybe tighten the wording" — be specific.
- Accepting a SKILL.md where Procedure is "use your judgment".
- Approving over the 200-char description limit "because it's almost there".
- Checking only the section headings — a skill whose Output example breaks its own rules teaches the model the wrong thing.
