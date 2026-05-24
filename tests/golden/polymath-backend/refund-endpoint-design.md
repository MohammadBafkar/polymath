---
plugin: polymath-backend
scenario: refund-endpoint-design
expect:
  invoked:
    - polymath-backend:api-design-rest
  output_matches:
    - "Idempotency-Key"
    - "201"
    - "409"
  not_invoked:
    - polymath-engineering:feature-dev
timeout_seconds: 120
---

# Prompt

> Design a refund endpoint.

Use the polymath-backend:api-design-rest skill. We need a REST
endpoint for issuing a refund against an existing order.
Constraints: callers may retry on timeout; partial refunds are
allowed; refunds can fail asynchronously (downstream provider).

# Acceptance

- The endpoint is `POST /v1/orders/{order_id}/refunds` or equivalently
  resource-oriented.
- Idempotency-Key header is required for the write.
- Status codes documented include 201, 400, 404, 409, 422, 429.
- Error envelope is named and structured.
- Request body uses integer amount (cents), not float.
