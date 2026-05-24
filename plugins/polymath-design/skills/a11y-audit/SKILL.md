---
name: a11y-audit
description: Audit a UI against WCAG 2.2 AA — perceivable, operable, understandable, robust; cite SC numbers + element selectors per finding.
---

# a11y-audit

> One audit pass on a UI surface against WCAG 2.2 AA. Findings cite the SC number, element selector, and a concrete remediation.

## When to use

- A new UI surface is being added.
- A PR touches an interactive surface and the team wants a structured a11y review.
- An issue report mentions "this isn't accessible" — pull this skill before responding.

## Inputs

- The UI surface: a route, a component path, or a screenshot + DOM.
- Optional: existing a11y findings to triage.

## Procedure

Walk the four POUR principles. For each, name applicable WCAG 2.2 AA Success Criteria (SC) and check.

1. **Perceivable**
   - SC 1.1.1 Non-text content — every image / icon / control has a text alternative (`alt`, `aria-label`, or `aria-labelledby`).
   - SC 1.3.1 Info and relationships — semantic HTML (`<button>`, `<nav>`, `<main>`, headings in order) — not all-`<div>`.
   - SC 1.4.3 Contrast — text vs background ≥ 4.5:1 (3:1 for large text). Check via computed style.
   - SC 1.4.10 Reflow — content reflows at 320 CSS px without horizontal scroll.
   - SC 1.4.11 Non-text contrast — UI components vs adjacent colors ≥ 3:1.
2. **Operable**
   - SC 2.1.1 Keyboard — every interactive element reachable + actionable via keyboard alone.
   - SC 2.4.3 Focus order — tab order matches visual order.
   - SC 2.4.7 Focus visible — visible focus indicator on every focusable element.
   - SC 2.5.5 / 2.5.8 Target size — interactive targets ≥ 24×24 CSS px (AA in 2.2).
3. **Understandable**
   - SC 3.2.2 On input — input changes don't trigger surprising context changes.
   - SC 3.3.1 Error identification — errors are named in text, not color alone.
   - SC 3.3.2 Labels or instructions — every form control has an associated label.
4. **Robust**
   - SC 4.1.2 Name, role, value — every interactive element exposes accessible name + role + state to assistive tech.
   - SC 4.1.3 Status messages — async status (toast, loading) announced via `role="status"` or `aria-live`.

For each finding cite **SC number + element selector + concrete fix**. Severity per WCAG: A > AA. AA is the target.

## Output

```text
A11y audit: <surface>

Critical (SC level A):
  - SC 1.1.1 — img.hero on /checkout has no alt. Fix: alt="Order
              summary illustration" or alt="" if decorative.
  - SC 2.1.1 — button.close (× icon) only handles click; Enter +
              Space not bound. Fix: use a <button> element instead
              of <div role="button">, or bind keydown.

Important (SC level AA):
  - SC 1.4.3 — .price-secondary text is #888 on #FFF (3.5:1).
              Below 4.5:1 AA. Fix: change color to #595959 or darker.
  - SC 2.5.8 — .delete-icon is 18×18 CSS px on mobile (below 24×24).
              Fix: bump touch target to 44×44 with transparent
              padding; visual icon can stay 18×18.

Status messages (SC 4.1.3):
  - "Saved" toast has no role/aria-live. Screen readers won't
    announce it. Fix: role="status".

Tooling note:
  Run axe-core in dev for automated coverage of ~50% of these criteria;
  axe doesn't catch reflow, focus order, or context-change SCs — those
  need this manual pass.
```

## Quality bar

- Every finding cites an SC number AND an element selector.
- Fixes are concrete (specific change), not "improve a11y".
- "Status messages" (SC 4.1.3) always checked — easy miss, big impact.
- AA is the bar. Don't flag AAA-only criteria as failures.

## Anti-patterns to avoid

- "Use axe / Lighthouse and call it done" — they catch ~50%, not 100%.
- ARIA-everywhere ("aria-label on every button"). Native semantics first.
- `tabindex="0"` on `<div>` instead of `<button>`. The fix is the element, not the attribute.
- Color-only error indicators (red border without text).
