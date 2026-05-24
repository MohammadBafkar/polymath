---
plugin: polymath-mobile
scenario: push-design-for-refunds
expect:
  invoked:
    - polymath-mobile:push-notifications
  output_matches:
    - "(opt-in|permission)"
    - "(transactional|marketing)"
    - "(quiet hours|deep-link|unsub)"
  not_invoked:
    - polymath-mobile:mobile-perf
timeout_seconds: 90
---

# Prompt

> Design push notifications for the refund flow.

Use polymath-mobile:push-notifications. We want to notify users when a
refund is initiated, completes, or fails. We do NOT want to send marketing
push for v0.1.

# Acceptance

- Opt-in moment is contextual, not at first launch.
- Channels: transactional default ON; marketing default OFF (explicit opt-in or absent).
- Per-channel toggles in-app.
- Tap deep-links to the specific refund, not the home screen.
- Quiet hours pinned (default).
- Unsub path in ≤ 2 taps documented.
- No PII / amounts in the visible body.
