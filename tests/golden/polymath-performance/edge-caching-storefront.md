---
plugin: polymath-performance
scenario: edge-caching-storefront
expect:
  invoked:
    - polymath-performance:http-edge-caching
  output_matches:
    - "(Cache-Control|s-maxage)"
    - "(Vary|cache key)"
    - "(private|no-store|purge)"
timeout_seconds: 120
---

# Prompt

> Put CloudFront in front of our storefront. Product pages change every few minutes, the cart is per-user, and our hit ratio is only 41%. Define the cache policy.

Use polymath-performance:http-edge-caching.

# Acceptance

- Per-content-class policy; personalized content bypassed.
- Cache key hygiene (tracking params, Vary: Cookie).
- Tag purge or versioned URLs; hit ratio measured per class.
