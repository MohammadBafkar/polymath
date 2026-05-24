---
name: prompt-engineer
description: Author or improve an LLM prompt — clarify task, constrain output shape, place worked examples, bound calibration; vendor-agnostic.
---

# prompt-engineer

> Write a prompt that gets the right answer with the lowest variance. Output is the prompt plus the reasoning behind each section.

## When to use

- A new prompt is being authored.
- An existing prompt has high variance or unreliable failure modes.

## Inputs

- The task in English (what should the model do, given what).
- The deployment shape: one-shot single-turn, multi-turn, tool-using agent, structured-output extractor.
- Available context: documents, examples, schemas.

## Procedure

1. **Task statement first**. The first sentence after any role framing is the task. Specific verb + specific deliverable: "Classify the message into one of [list]" beats "Help me categorize this".
2. **Output shape**. Pin it explicitly:
   - JSON schema (and refuse non-JSON in the prompt).
   - Markdown sections (named).
   - One-of-N (give the list).
3. **Inputs section**. Label every input with a heading so the model can reference them. `<message>...</message>` style tags work across vendors.
4. **Constraints in priority order**:
   - What it MUST do.
   - What it MUST NOT do.
   - Soft preferences last.
5. **Worked examples** if the task allows variance. 2–4 examples that span the space. Place them near the bottom; the model attends to recent context more.
6. **Calibration line**: tell the model when to say "I don't know" or to abstain. Otherwise it confabulates.
7. **Cost trim**. Cut tokens that don't change the answer. Remove:
   - "You are a helpful assistant" filler.
   - Multiple ways of saying the same constraint.
   - Examples that test the same axis twice.

## Output

```text
Prompt:
---
You will classify an inbound support message into exactly one category from:
[billing, technical, account, abuse, other].

Output JSON only, matching:
{ "category": "<one-of-the-five>", "confidence": "high" | "low" }

Rules:
- If the message touches multiple categories, pick the one most relevant to
  the user's *primary* ask.
- If you cannot determine a category from the message alone, output
  category="other", confidence="low". Do NOT guess.

Examples:
<message>I was charged twice for the same order.</message>
{ "category": "billing", "confidence": "high" }

<message>The app crashes when I open settings.</message>
{ "category": "technical", "confidence": "high" }

<message>hi</message>
{ "category": "other", "confidence": "low" }

Now classify:
<message>{{user_message}}</message>
---

Reasoning per section:
- Task in the first sentence; verb "classify"; deliverable "one category".
- Output shape pinned to JSON with the legal categories enumerated.
- Calibration line guards against confabulation.
- 3 examples spanning billing / technical / abstention.
```

## Anti-patterns to avoid

- "You are an expert" framing — adds tokens, doesn't change behavior.
- Polite filler ("please", "thank you").
- Examples that all test the same axis.
- "Be creative" plus a strict schema — pick one.
