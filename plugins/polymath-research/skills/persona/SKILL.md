---
name: persona
description: Author a persona grounded in ≥ 5 real interviews; verbatim quotes, named anti-persona, no composite stock personas.
---

# persona

> Distill a persona from real conversations. No persona before 5 interviews; no composite stock characters.

## When to use

- A team has run at least 5 customer interviews and wants to lock the patterns.
- Existing "personas" in the company are stock vendor templates that nobody references — write a real one to replace them.

## Inputs

- The set of 5+ interview transcripts or notes.
- Recruit metadata (role, context).

## Procedure

1. Read [`Persona.md`](../../templates/Persona.md) (materialized from `shared/templates/`).
2. Compute the slug from the persona's defining characteristic (e.g. `solo-platform-engineer`, not `power-user`).
3. Draft `docs/research/personas/<slug>.md`:
   - **Role and context** — including what they're doing in the 30 seconds before and after they touch your product.
   - **Goals** — what *they* are paid to achieve. Not what your product is paid to do.
   - **Frustrations (verbatim)** — at least 3 direct quotes from interviews. No paraphrasing.
   - **Current workaround** — concrete, not "they manage somehow".
   - **What would make them switch** — what they told you, not what you wish they wanted.
   - **Anti-persona** — name who this excludes.
   - **Evidence table** — N ≥ 5 rows linking quotes to interview IDs.

## Quality bar

- 5+ interviews referenced in the Evidence table. Refuse to ship a persona below this bar.
- All quotes verbatim. No "the user said something like …".
- Goals are the persona's goals (their job description), not the product's goals.
- Anti-persona present.

## Output

- File: `docs/research/personas/<slug>.md`.
- Summary listing N of evidence interviews + a one-line characteristic ("solo platform engineer at a 20-person startup who owns CI, k8s, and on-call").

## Anti-patterns to avoid

- "Personas from internal stakeholders' opinions." Not research.
- Composite: blending three real interviewees into "the average user". The average loses the signal.
- Demographic-led personas (age, gender) instead of behavior-led.
- One persona for the whole product. Most products have 2–4.
