---
name: mobile-perf
description: Set mobile perf budgets — cold start (TTI), warm start, scroll FPS, memory; per audience device tier (low-end Android baseline); identify the dominant cost. Native only; not web CWV.
---

# mobile-perf

> Mobile perf is about the low-end Android in someone's hand, not the iPhone on your desk. Output is a budget per critical screen + the dominant cost.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- A mobile app or screen is being designed/built.
- Users complain "the app is slow" but the team doesn't know which axis.

## Inputs

- The critical screens/journeys (required) and the platforms.
- Field data (optional but decisive): Play Console vitals, Xcode Organizer, Firebase Performance, Sentry — absent, the budget is a target to measure against, and the "dominant cost" line is `[TBD: profile on the audience device]`, never guessed.
- The audience device tier (required — see below); unknown → low-end Android baseline.

## The budget axes

For each critical screen / journey, pin all four:

- **Cold start TTI**: app launched fresh → first interactive frame. Target: < 2s on low-end Android.
- **Warm start TTI**: app foregrounded from background. Target: < 500ms.
- **Scroll FPS**: target 60 fps on lists; flag if < 55 sustained.
- **Memory ceiling**: target stays under the OS's foreground-app memory bucket for the audience device (typically 200–400 MB on low-end Android).

## Audience device tier

Pin which device represents the audience. The fastest dev phone in the office is not it.

- **Low-end Android baseline**: an entry-level device a few years old — 3–4 GB RAM, budget SoC (Galaxy A0x/A1x-class). This is where a large share of real users are.
- **Median Android**: a mid-range device ~2–3 years old (Galaxy A5x-class, 6–8 GB RAM) — not a flagship.
- **High-end**: a current flagship — useful as a ceiling, never as the budget device.
- **iPhone tier**: current iPhone or 2–3-year-old iPhone — much smaller perf variance than Android.
Use your own analytics' device distribution when you have it.

For consumer apps, low-end Android is almost always the right baseline.

## Procedure

1. **Pick the screen / journey** (one at a time; multiple screens = multiple passes).
2. **Pin the 4 axes** with target values.
3. **Measure current state** with the audience device tier. Real device, release build, not simulator — Android: Macrobenchmark / Perfetto traces and Play Console Android vitals; iOS: Instruments and MetricKit field data.
4. **Identify the dominant cost** of any axis missing its target. Common culprits:
   - **Cold start**: too many libraries loaded synchronously, premature DB warm-up, oversized launch storyboard.
   - **Warm start**: app re-initializes state instead of restoring it.
   - **Scroll FPS**: heavy item rendering, missing recycling, layout thrash, JS thread blocking (RN/Flutter).
   - **Memory**: bitmap caching unbounded, leaks in adapter/list controllers, large hero images undowngraded.
5. **Recommend ONE fix** with expected effect.

## Output

```text
Mobile perf budget: /home screen (cold start)

Audience device: low-end Android (Galaxy A14-class, 4 GB RAM, budget SoC).

Targets:
  Cold start TTI    : < 2,000 ms
  Warm start TTI    : <   500 ms
  Scroll FPS        : ≥ 55 fps
  Memory (foreground): < 250 MB

Current (measured on that device, battery saver off, release build, Macrobenchmark median of 10):
  Cold start: 3,400 ms   ← over budget
  Warm start:   380 ms   ok
  Scroll FPS :  58 fps   ok
  Memory     : 210 MB    ok

Dominant cost (cold start):
  4 SDKs are initialized synchronously in onCreate (analytics, push, crash,
  feature flags). Together ~1,600 ms.

First fix:
  Move 3 of 4 SDKs to async init after the first frame. The crash SDK stays
  synchronous (must capture early crashes). Expected: cold start ~1,800 ms,
  under target. Validate on the same device and build.
```

## Quality bar

- Audience device tier pinned (real device name).
- All 4 axes have target + measured value.
- One dominant cost named for any failing axis.
- One first fix with expected effect.

## Anti-patterns to avoid

- Measuring on this year's flagship and shipping.
- Optimizing scroll FPS when cold start is failing. Fix the failing axis first.
- "Add a splash screen" to hide cold start. Hides the symptom; doesn't fix it.
- Single-axis budget. Always pin all 4.
