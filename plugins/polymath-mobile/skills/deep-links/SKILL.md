---
name: deep-links
description: Design deep-link routing — universal/app links over custom schemes, deferred deep-link for install path, fallback web URL, signed param verification.
---

# deep-links

> Deep links bridge web + push + email into the app at the right screen. Output is a routing table + the fallback web URL + the verification story.

## When to use

- A new app or major feature ships and the team needs to support inbound deep links.
- Push payloads need a routing target (see `push-notifications`).
- Marketing wants email links to open the app.

## Mechanism choice

- **Universal Links (iOS) + App Links (Android)** — preferred. Verified via apple-app-site-association / assetlinks.json. URL is a plain https URL; opens the app if installed, the web page otherwise.
- **Custom URL schemes** (`myapp://...`) — deprecated for primary use. Can be hijacked; no verification. Only use as a fallback.
- **Deferred deep links** (e.g. via attribution SDK or first-party server) — needed when the user clicks a link before installing the app. Captures intent during install so the app routes correctly on first open.

## Procedure

1. **Define a URL scheme** — humans see https://example.com/refunds/<id> in their email, and the app handles `/refunds/<id>`.
2. **Set up verification**:
   - iOS: serve `/.well-known/apple-app-site-association` (AASA). Include the paths the app handles.
   - Android: serve `/.well-known/assetlinks.json`. Include the package name + SHA-256 of the signing key.
3. **Routing table** in the app:
   ```
   /refunds/:id              → RefundDetailScreen(refund_id)
   /orders/:id               → OrderDetailScreen(order_id)
   /orders/:id/refunds/new   → NewRefundScreen(order_id)
   /share/:token             → ShareLandingScreen(token) — public unauth path
   ```
4. **Auth-gated screens**: deep link → if signed-in, go to screen; if not, signed-out landing → after login, complete the deep link. **Never** drop the user on the home screen after auth.
5. **Deferred deep-link support**: pre-install link click captured by the attribution SDK or by a first-party landing URL (server-side log + cookie). On first launch after install, app fetches the pending deep link and routes.
6. **Parameter verification**: signed/JWT params for sensitive operations (e.g. magic-link login, password reset). Treat deep-link inputs as **untrusted**; verify on the server.
7. **Fallback web URL**: every deep link MUST have a working https URL that handles the case when the app isn't installed. Quality of the fallback is a feature.

## Output

```text
Deep-link design: refund-service

URL space:
  https://example.com/refunds/<refund_id>
  https://example.com/orders/<order_id>
  https://example.com/orders/<order_id>/refunds/new
  https://example.com/share/<share_token>

Verification:
  iOS:     /.well-known/apple-app-site-association (paths: /refunds/*, /orders/*, /share/*)
  Android: /.well-known/assetlinks.json (package: com.example.refund, SHA-256: <fingerprint>)

Routing (in-app):
  /refunds/:id            → RefundDetail   (auth required; resume after login)
  /orders/:id             → OrderDetail    (auth required; resume after login)
  /orders/:id/refunds/new → NewRefund      (auth required)
  /share/:token           → ShareLanding   (public; token JWT-verified)

Auth-gated:
  Save target URL → signed-in flow → on success, complete the original deep
  link instead of going home.

Deferred deep links:
  Server-side: first-party landing URL captures the intent + sets a 1-day
  cookie. App on first launch fetches /pending-deep-link with the cookie.

Untrusted-input contract:
  All :id and :token params are validated server-side. The share-token is a
  short-lived JWT signed with our key.

Fallback web URL:
  Every URL works in a browser. /refunds/<id> renders a read-only HTML
  receipt for users without the app. Quality of the fallback is in scope.
```

## Quality bar

- Universal/App Links over custom schemes for primary inbound.
- AASA + assetlinks.json files served from the actual domain.
- Auth-gated routes resume the deep link after login (don't dump to home).
- Sensitive params verified server-side; treat all deep-link input as untrusted.
- Fallback web URL works.

## Anti-patterns to avoid

- `myapp://` as the only entry point. Hijackable; no verification.
- Routing param trusted without server-side validation.
- After-login redirect drops user on home, losing the deep-link intent.
- No fallback web URL — half your audience can't open it.
- Deferred deep links handled "best effort"; if they're load-bearing, validate.
