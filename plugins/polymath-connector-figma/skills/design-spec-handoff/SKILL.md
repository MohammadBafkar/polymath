---
name: design-spec-handoff
description: Convert a Figma frame URL into a build-ready spec — layout, tokens used, states, copy, interactions, and what's missing.
---

# design-spec-handoff

> Read a Figma frame and produce a build-ready spec a frontend engineer can implement from without flipping back to Figma every five minutes. Output names every component used, every state covered, every state missing, and every design-token reference.

## When to use

- A PRD references a Figma frame and engineering needs an implementation spec.
- A `polymath-product:prd` is in review and the design column is "see Figma" — needs translation.
- A handoff is happening cross-timezone and questions can't be asked in real time.

## Inputs

- Figma frame URL (required) — must point to a specific frame node, not just a file.
- Target platform (required) — web / iOS / Android / cross-platform. Drives unit + density conventions.
- Design system (optional) — name of the system whose tokens should resolve (e.g. `acme-ds-v3`).

## Procedure

1. **Resolve the file + node IDs** from the URL (`?node-id=` query param). Refuse vague file-root URLs — they hide which frame is the source of truth.
2. **Fetch the frame** via the figma MCP's `file.getNode` (or equivalent). Pull children, styles, and component references.
3. **Enumerate components used.** For each instance, name the design-system component + variant. Flag any "detached" instances (overrides outside the system) as a spec defect, not a build instruction.
4. **Extract design tokens.** Map raw values to token names where possible: colors → `color/*`, spacing → `space/*`, type → `text/*`. Raw values that don't map to a token are flagged for design review.
5. **Enumerate states.** For each interactive surface, list which states are designed:
   - **Required:** default, hover, pressed/active, focus-visible, disabled.
   - **Conditional:** loading, empty, error, success.
   - **Mark missing states explicitly** — silence is the most common handoff bug.
6. **Capture copy verbatim.** Strings go through localization, not engineer paraphrase. If a string is missing, mark it; do not invent.
7. **Capture interactions** — transitions, animations, gestures. Reference the prototype connection if Figma provides one; otherwise note "no prototype defined; behavior must be specced in PRD."
8. **Accessibility crosscheck.** Surface contrast ratios for text/background pairs, minimum tap targets, focus order if defined.
9. **Output the spec** as structured Markdown an engineer can paste into a PR description.

## Output

```text
design-spec-handoff: Refund detail card (acme-app/Frame:refund-card)

Source:     https://www.figma.com/file/<file-id>?node-id=42:108
Platform:   web (rem-based)
System:     acme-ds-v3

Components used:
  - Card/elevated                                       (1 instance, no overrides)
  - Button/primary    variant=destructive               (1 instance)
  - Tag/status        variant=warning                   (1 instance)

Tokens:
  - bg:        color/surface-2
  - title:     text/heading/md  + color/text-primary
  - meta:      text/body/sm     + color/text-muted
  - spacing:   space/200 between sections

States designed:    default, hover, disabled, loading
States MISSING:     focus-visible, error, empty
  → blocks accessibility audit; request from designer before build.

Copy (verbatim):
  - title:      "Refund $%amount%"
  - cta:        "Issue refund"
  - cancel:     (missing — request from design)

Interactions:
  - On submit: spinner replaces CTA label; card disables; success state navigates back to list.
  - No prototype connection defined for the failure path.

Open questions:
  - Designer detached the Button instance to override icon — re-attach or update component?
```

## Quality bar

- Frame URL includes a `node-id`; file-root URLs are rejected.
- Every component instance named with variant.
- Missing states listed explicitly.
- Copy strings are verbatim, never paraphrased.
- Accessibility surfaces (contrast, focus order) are at least addressed.

## Anti-patterns to avoid

- Spec'ing from a screenshot. Pixel-counting loses state, token, and copy information.
- Inventing copy strings to "fill in" what designers forgot. Always flag the gap.
- Treating a detached instance as authoritative. It's a defect; surface it.
- Listing only the designed states without flagging the missing ones. The gap is the whole point of handoff.
