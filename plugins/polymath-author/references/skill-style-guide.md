# Polymath SKILL.md style guide

Every SKILL.md in the marketplace follows this shape. The structure is what
makes `skill-author-critic` work; deviating from it removes the benefit of
the review.

## Required structure

```markdown
---
name: <kebab-case>          # must match the skill directory name
description: <≤ 200 chars; imperative verb first; says when this triggers>
---

# <name>

> One-line blockquote summarizing the skill in the user's voice. Imperative;
> not "this skill does X".

## When to use

- 2–4 concrete user phrases or workflow positions.
- Each bullet is specific ("the user says 'review this'", not "the user wants to review").

## Inputs

- Required vs optional. State defaults when absent.

## Procedure

1. Numbered. Observable. Decisive.
   - Sub-bullets only when a step has multiple sub-decisions.
2. No "consider X" — consider what, and what decides?
3. Cite frameworks (DORA, SLO, RED/USE, STRIDE) by their canonical name.

## Output

Show the exact shape via a fenced code block. The model imitates this; if
it's vague, output is vague.

## Quality bar  (or "Anti-patterns to avoid")

- 3–6 bullets covering easy-mode failures.
- Make it specific to *this* skill, not generic "write clean code".
```

## Frontmatter rules

| Field         | Required | Notes                                                              |
| ------------- | -------- | ------------------------------------------------------------------ |
| `name`        | yes      | kebab-case. Must equal the skill directory name.                   |
| `description` | yes      | ≤ 200 chars. Leads with an imperative verb. Says when it triggers. |

Optional fields (v0.2+, must be verified against current Claude Code docs
before relying):

- `disable-model-invocation: true` — manual-only side-effect skills.
- `paths: [glob]` — language-specific skills only attached on matching files.
- `allowed-tools: <list>` — limit the toolset the skill is allowed to use.

## Length

- SKILL.md body ≤ 500 lines.
- Spill reference material to `references/<topic>.md` siblings.
- Skills that need more than 500 lines are almost always two skills.

## Naming

- Files: `SKILL.md` (capitalized, no extension variant).
- Directory: kebab-case, matches `name:`.
- Single-word names are allowed (`brainstorm`, `dockerize`); compound names
  hyphenated (`stride-threat-model`).

## Cross-skill references

- Link other skills as `polymath-<plugin>:<skill>`. Do not invoke them as
  programmatic slash-commands — they're routing labels.
- When a skill builds on another, name it in the Procedure section
  ("after `polymath-engineering:read-code` orients").

## Anti-patterns rejected by `skill-author-critic`

- Description that starts with "This skill" or "A skill that".
- Description over 200 chars.
- Missing "When to use".
- Procedure that says "use your judgment" without naming the decision.
- No "Output" section. The model has nothing to imitate.
- No anti-patterns / quality-bar section. Easy-mode failures will happen.
- Body > 500 lines.
- Comments narrating what the next paragraph will explain.
