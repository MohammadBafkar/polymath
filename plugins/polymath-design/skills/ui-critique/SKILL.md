---
name: ui-critique
description: Critique a UI surface — hierarchy, density, error/empty/loading states, microcopy; findings keyed to specific elements with concrete corrections.
---

# ui-critique

> Critique one UI surface. Output is findings keyed to specific elements, not "feels off".

## When to use

- A design has been mocked or implemented and the team wants a second pass before ship.
- An existing surface has user complaints but the team can't name why.
- A workflow's design-review step needs a structured critique.

## Procedure

For each of these axes, scan the surface and emit findings:

1. **Visual hierarchy**
   - The single most-important thing on the page is the visually-loudest. If the headline is dimmer than a sidebar promo, fix it.
   - Type scale uses 3–5 sizes, not 12. If the page has 12 different text sizes, it has none.
2. **Density**
   - White space is content. A wall of dense text needs grouping.
   - A wall of icons + labels needs prioritization. Demote secondary actions to a `…` menu.
3. **States**
   - **Loading**: skeleton or spinner? Skeleton when content shape is predictable; spinner when it's not.
   - **Empty**: the empty state is a teaching opportunity — what should the user do next?
   - **Error**: error names what's wrong + what to do, in user words. Never "An error occurred."
   - **Partial**: long lists fade or paginate honestly; don't pretend the page is the whole result.
4. **Microcopy**
   - Buttons are verbs: "Cancel order", not "Cancel" alone when both buttons say "Cancel".
   - Confirmation dialogs name the consequence: "Delete 12 invoices? This can't be undone." not "Are you sure?"
   - Form labels above fields (faster scan than left-side); placeholders are NOT labels.
5. **Affordances**
   - Looks-clickable → is-clickable. If text is blue and underlined, it's a link.
   - Disabled controls give a reason ("Add 1 more user to enable") not just gray-out.

## Output

```text
UI critique: <surface>

Visual hierarchy:
  - The "Buy" CTA on /checkout is visually lighter than the "Continue
    shopping" link directly above. Loudest element should be the
    primary action. Fix: bump CTA contrast / weight; demote the link.

Density:
  - Sidebar shows 12 secondary actions inline. Move 8 to an overflow
    "…" menu; keep the 4 most-used inline.

States:
  - Empty state of /orders is "No orders." Plus the page is blank.
    Add a one-line nudge: "When you place your first order, it'll
    appear here." Add a link to the catalog.
  - Error toast says "An error occurred." Replace with the specific
    failure ("Couldn't reach the payment provider — try again in a
    moment").

Microcopy:
  - Both modal buttons say "Cancel". Rename the destructive one
    "Cancel order" and the dismiss one "Keep shopping".

Affordances:
  - .row-action looks like static text. If it's clickable, give it
    cursor: pointer + an underline on hover.
```

## Quality bar

- Every finding names a specific element (CSS selector, mock annotation, or "the CTA on /route").
- Fixes are concrete corrections, not "improve hierarchy".
- States section always checked (most common skip).
- Microcopy quotes the offending string verbatim.

## Anti-patterns to avoid

- Generic complaints ("feels cramped"). Specify what's cramped.
- Suggesting a redesign when 3 tweaks would fix it.
- Approving a design that has no empty/error states drawn.
- "Add more whitespace" without naming where; whitespace is a tool, not a panacea.
