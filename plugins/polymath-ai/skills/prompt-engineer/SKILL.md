---
name: prompt-engineer
description: Author or improve an LLM prompt — clarify task, constrain output shape, place worked examples, bound calibration; vendor-agnostic.
---

# prompt-engineer

> Write a prompt that gets the right answer with the lowest variance. Output is the prompt plus the reasoning behind each section.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

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
   - JSON: prefer the API's native structured output / tool schema when the provider has one; otherwise give the schema in the prompt, then parse and validate the reply and retry on failure — never assume it parsed.
   - Markdown sections (named).
   - One-of-N (give the list).
3. **Inputs section**. Label every input with a heading so the model can reference them. `<message>...</message>` style tags work across vendors.
4. **Constraints in priority order**:
   - What it MUST do.
   - What it MUST NOT do — but phrase rules positively where you can ("reply in plain prose" beats "don't use Markdown").
   - Soft preferences last.
   Give the *reason* behind non-obvious constraints ("answers are read aloud by a TTS engine, so no lists") — models generalize from the why.
5. **Worked examples** if the task allows variance. 2–4 examples that span the space, wrapped in tags (`<example>`) so they read as examples, not instructions. Long reference documents go at the top of the prompt and the question at the end.
6. **Reasoning room** for multi-step tasks: let the model think before the final answer (or enable the provider's extended thinking), and ask for the answer in a separate tagged block so it's easy to parse. Skip it for simple classification where latency matters.
7. **Calibration line**: tell the model when to say "I don't know" or to abstain. Otherwise it confabulates.
8. **Compare two drafts** when the task has real variance: write a second draft that differs in approach (few-shot vs rules-first, or reasoning block vs none), not just wording, and keep whichever scores better on the eval set.
9. **Test it**: run the prompt against a small labeled set (`polymath-ai:eval-plan`) before and after each change; keep the failures as regression cases. A prompt tuned on vibes regresses silently.
10. **Cost trim**. Cut tokens that don't change the answer. Remove:
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

- Generic "You are a world-class expert" framing in place of real context — a specific role (audience, domain, constraints) helps; flattery doesn't.
- Shouting (ALL-CAPS "MUST", "CRITICAL") to fix a rule the model ignores — explain the reason instead; capable models over-apply shouted rules.
- Examples that all test the same axis.
- "Be creative" plus a strict schema — pick one.
