---
plugin: polymath-design
scenario: a11y-audit-checkout
expect:
  invoked:
    - polymath-design:a11y-audit
  output_matches:
    - "SC [0-9]"
    - "(contrast|focus|label|aria)"
    - "Fix:"
  not_invoked:
    - polymath-engineering:feature-dev
timeout_seconds: 120
---

# Prompt

> Audit the checkout page for a11y.

Use polymath-design:a11y-audit. The page has:
- A hero image without alt text.
- A "Buy" button styled as a <div role="button"> with only click handlers.
- .price-secondary text is #888 on white background (3.5:1 contrast).
- The "Saved" toast has no role or aria-live.

# Acceptance

- Each finding cites a WCAG SC number (e.g. SC 1.1.1, SC 2.1.1, SC 1.4.3, SC 4.1.3).
- Each finding names the element selector and a concrete fix.
- Severity per WCAG level (A vs AA) is distinguished.
- Status messages (SC 4.1.3) flagged for the toast.
- No suggestion to "just run axe and call it done".
