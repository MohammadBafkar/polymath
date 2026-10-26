---
name: api-design-rest
description: Design a REST endpoint or resource — URL, method, status codes, request/response shape, errors, idempotency, versioning.
---

# api-design-rest

> Specify a REST endpoint before implementing it. Output is a one-page design that surfaces the trade-offs.

## When to use

- Adding a new endpoint.
- An existing endpoint's contract is ambiguous and a caller asks "what does this do?".
- A workflow invokes `polymath-backend:api-design-rest`.

## Inputs

- Resource and operation in plain English.
- Existing API conventions in the repo (read the most recent endpoint).

## Project localization

Before the procedure, resolve the project snapshot —
`${POLYMATH_DATA_DIR:-$HOME/.polymath/data}/polymath-core/project-context.json`
(ignore it if its `_meta.source` belongs to another repo; absent → read
`.polymath/project.yaml` directly; neither → built-in defaults). Then apply
(contract: `polymath-core:project-context`):

- `conventions_docs`: read roles `api-style` and `backend-stack`; follow
  `conventions.api_style_guide` when set. Project rules win over the
  generic defaults below.

## Procedure

1. **Resource shape** — name the resource (noun, plural) and its identifier scheme. URLs operate on resources, not actions: `POST /orders/:id/refunds` ≫ `POST /refundOrder`.
2. **AuthN + AuthZ** — the scope/role required, and the object-level check: the caller may act on *this* `:id` (broken object-level authorization is the most common API vulnerability). Decide 403 vs 404 for "exists but not yours" — 404 avoids confirming the resource exists.
3. **Method** — choose by semantics, not by accident:
   - GET — safe, idempotent, cacheable.
   - POST — create / non-idempotent action.
   - PUT — full replace (idempotent).
   - PATCH — partial update (idempotent if the patch is value-based; not if it's "append").
   - DELETE — idempotent.
4. **Status codes** — pick from this short list and stick to it:
   - 200 OK (response has body), 201 Created (with Location), 202 Accepted (async work), 204 No Content (no body).
   - 400 Bad Request (validation), 401 Unauthorized (no/invalid creds), 403 Forbidden (creds OK but not allowed), 404 Not Found, 409 Conflict (concurrent edit / unique constraint), 410 Gone, 422 Unprocessable Entity (semantic validation), 429 Too Many Requests.
   - 500 Internal Server Error, 503 Service Unavailable (retry hint via Retry-After).
5. **Request/response shape** — JSON. snake_case OR camelCase, pick one for the whole service. Show one happy-path example.
6. **Errors** — one error envelope for the whole service (RFC 9457 `application/problem+json` is the standard option if the service has none yet):

   ```jsonc
   { "error": { "code": "RATE_LIMIT_EXCEEDED", "message": "…", "details": { "retry_after_seconds": 60 } } }
   ```

   `code` is machine-readable, `message` is human-readable, `details` is structured context. Don't surface stack traces.
7. **Idempotency** — for `POST` (and non-idempotent `PATCH`) writes that may be retried: require an `Idempotency-Key` header. (`PUT` and `DELETE` are idempotent by definition.) Store the request fingerprint and response against the key for ≥ 24h; a reused key with a *different* payload returns `422`, and a request arriving while the first is still in flight returns `409`.
8. **Versioning** — pick one and stick to it: URL (`/v1/orders`) or header (`Accept: application/vnd.example+json; version=1`). URL is simpler and works with caches.
9. **Pagination** — cursor-based for collections that can grow. Page size capped server-side; expose `next_cursor` in the response.
10. **Rate limit signaling** — `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset` headers (or the legacy `X-` variants if the service already uses them).

## Output

```text
Endpoint: POST /v1/orders/:order_id/refunds

Purpose: Initiate a refund for an order.

Auth: Bearer (scope=orders:refund).
Idempotency: required (Idempotency-Key header).

Request body:
  { "amount_cents": int, "reason": string, "refund_to": "original"|"credit" }

Responses:
  201 Created         { "refund": { "id": "...", "status": "processing", ... } }
  400 Bad Request     amount_cents not int / missing reason
  404 Not Found       order_id unknown
  409 Conflict        order already fully refunded
  422 Unprocessable   amount_cents exceeds order total
  429 Too Many Requests  (Retry-After: 60)

Errors envelope: standard. Codes used: VALIDATION, ORDER_NOT_FOUND,
ALREADY_REFUNDED, EXCEEDS_TOTAL, RATE_LIMIT.
```

## Anti-patterns to avoid

- Verbs in URLs (`/getOrder`).
- 200 OK for everything (use 201/204 where appropriate).
- "Errors" returned as 200 with an `error` field in body.
- Surfacing internal IDs / stack traces in error responses.
- Skipping idempotency on a payment / refund / send-email endpoint.
- Checking that the caller is logged in but not that they own the `:id` they're acting on.
