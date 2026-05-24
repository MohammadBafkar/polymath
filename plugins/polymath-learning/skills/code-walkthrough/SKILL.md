---
name: code-walkthrough
description: Walk through a piece of code in execution order for a given audience — entry point, branches, side effects, the surprising line; cite file:line.
---

# code-walkthrough

> Trace one execution path through real code. Output is a guided narrative the reader can follow with the source open beside them.

## When to use

- A new contributor needs to understand how X works.
- A code-review reviewer wants the diff narrated.
- A workflow needs onboarding-ready text.

## Inputs

- Path/glob into the code (required).
- Audience tier (per the `explain` skill).
- Optional: a specific entry point (a function, a route, a test).

## Procedure

1. **Find the entry point**. The CLI command, the HTTP route, the test that exercises the path.
2. **Trace execution in order**. Each step: file:line → what happens there → why (if non-obvious).
3. **Call out side effects** — when the path touches the DB, the filesystem, the network, a global, a cache. These are where bugs live.
4. **Find the surprising line**. Every walkthrough has one. Name it and explain why it's there (often a workaround for something).
5. **Skip the obvious**. Loops over arrays don't need narration. Custom error handling does.
6. **Audience tier**: for less-experienced audiences, expand prerequisites inline; for peer audiences, link them.

## Output

```text
Code walkthrough: <entry point> — audience: <tier>

Step 1: [file.py:42] receives the request
  Inputs: …
  What it does: …

Step 2: [file.py:78] validates the auth
  Why this not in middleware: <reason, often a quirk>

Step 3: [util.py:15] formats the output
  Side effect: writes to <cache key>

Surprising line:
  [file.py:103] — `if x is None or x == "":` looks redundant; it's there
  because legacy callers in pre-1.0 send "" while new callers send None.

Where the bugs tend to live:
  - <file:line> — race between cache write and read.
  - <file:line> — silent fallthrough when auth missing.
```

## Quality bar

- Every step cites file:line.
- Side effects called out specifically (cache key, DB table, file path).
- One "surprising line" called out per walkthrough.
- Doesn't narrate obvious code; skips to the interesting parts.

## Anti-patterns to avoid

- "Line-by-line" narration of the whole file. Skim what's obvious.
- No file:line citations. The reader can't follow.
- Hiding the surprising line. That's the one the reader most needs to know about.
- Walkthrough that tries to cover three execution paths at once.
