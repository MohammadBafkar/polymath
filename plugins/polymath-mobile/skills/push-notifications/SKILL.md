---
name: push-notifications
description: Design push notifications — opt-in moment, payload shape, tap-deep-link, silent vs visible, quiet hours, unsub path; respect the OS bucket constraints.
---

# push-notifications

> Push is one of the easiest privileges to abuse. Output is the design that earns and keeps the permission — payload, timing, and the unsub path.

## When to use

- A new app or feature is introducing push notifications.
- An app's push opt-in rate / unsub rate has regressed.
- A workflow's user-engagement step needs structured push design.

## Procedure

1. **Opt-in moment**: never on app launch. Ask after the user has experienced enough value to want the notification. The contextual opt-in ("Get notified when your refund clears") wins over the cold OS prompt.
2. **Two channels minimum**:
   - **Transactional**: order updates, refund status, password resets. Default ON.
   - **Marketing / engagement**: discounts, "we miss you". Default OFF; explicit opt-in.
   Make the user able to toggle each independently in-app.
3. **Payload shape** — both iOS APNs and Android FCM:
   - `title`: scannable headline (≤ 32 chars on most lockscreens).
   - `body`: 1–2 short sentences.
   - `data`: structured fields the app uses to deep-link (e.g. `{"type": "refund_complete", "refund_id": "ref_…"}`). Do **not** put PII or amounts in `data`; minimize what the OS can persist.
4. **Tap behavior**: deep-link to the specific entity, not the home screen. "Refund processed" tap → /refunds/<id>, not /.
5. **Silent vs visible**:
   - **Visible**: user-facing. Must have user value beyond "your app exists".
   - **Silent (data-only)**: app processes in background. iOS APNs limits volume; Android FCM has Doze constraints. Don't use silent push for engagement.
6. **Quiet hours**: respect them. Default 22:00–08:00 user-local for non-time-sensitive notifications. Tag time-sensitive (e.g. iOS `interruption-level: time-sensitive`) only when warranted.
7. **Unsubscribe path**: in-app settings reachable in ≤ 2 taps. Per-channel toggles. Honor "do not contact" as the strict-deny default.
8. **Tracking**: delivery rate, open rate, action rate, unsub rate. Alert when unsub rate doubles week-over-week.

## OS constraints to respect

- **iOS APNs**: priority 10 (immediate) vs 5 (when convenient). Don't use 10 for marketing.
- **Android FCM**: high vs normal priority. High priority delivered through Doze; over-use gets the app reputation-flagged.
- **Provisional auth (iOS)**: send to Notification Center without prompt; user promotes if useful. Good for low-stakes channels.

## Output

```text
Push design: refund-service

Channels:
  Transactional (default ON):
    - refund_initiated, refund_complete, refund_failed.
  Marketing (default OFF, explicit opt-in):
    - none for v0.1.

Opt-in moment:
  After the user views the refund-status page once. Contextual prompt:
  "Get notified when your refund clears."

Payload shape (refund_complete example):
  title: "Refund complete"
  body:  "Your refund for order #1234 is on its way to your bank."
  data:  { type: "refund_complete", refund_id: "ref_…" }
  iOS interruption-level: active (not time-sensitive).
  Android priority: normal.

Tap behavior:
  Deep-link to /refunds/<refund_id>.

Quiet hours:
  22:00–08:00 user-local for all marketing; transactional respects unless
  the user opted into time-sensitive.

Unsubscribe path:
  Settings → Notifications → Refund updates toggle. Per-channel.

Tracking + alerts:
  Alert: unsub rate doubles WoW for any channel → review the recent change.
```

## Quality bar

- Opt-in is NOT at first launch.
- At least two channels with independent per-channel toggles.
- Tap deep-links to the entity, not the home.
- Quiet hours pinned.
- Unsub path reachable in ≤ 2 taps.

## Anti-patterns to avoid

- Asking permission at app launch. Burns the only chance.
- One push channel for all notifications. User has to choose all-or-nothing.
- PII / amounts in the visible body that show on the lockscreen.
- Silent push for "engagement" — wastes battery and gets the app throttled.
- No unsub in-app, only via OS toggle. Frustrating; they'll uninstall.
