---
name: http-edge-caching
description: Design HTTP, CDN and edge caching — Cache-Control, cache keys, Vary, purge, stale-while-revalidate. Not Redis (design-cache-layer).
---

# http-edge-caching

> The cheapest request is the one your origin never sees. Cache at the edge deliberately: decide what is cacheable, for whom, for how long, and how it gets invalidated — and never cache what is personal by accident.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- Putting a CDN/reverse proxy (CloudFront, Cloudflare, Fastly, Akamai, Azure Front Door, nginx/Varnish) in front of an app or API.
- Origin load or egress cost is high for content that changes rarely; or users far from the origin see slow loads.
- Stale content after deploys, personalized data leaking through a cache, or a low edge hit ratio.

Not this when: the cache is application-side (Redis, in-process) — `polymath-performance:caching-tradeoffs` / `design-cache-layer`. Browser Core Web Vitals budgets — `polymath-frontend:web-vitals-budget`.

## Inputs

- Routes/content classes with: change frequency, personalization (anonymous, per-user, per-tenant, per-locale), size, and acceptable staleness (a product decision — ask, or propose and mark `[VERIFY: staleness]`).
- The current response headers per class, CDN/proxy config, and the edge hit ratio and origin offload (CDN logs/analytics).
- Deploy process (asset fingerprinting?), auth model (cookies/tokens), regions.

## Procedure

1. **Classify content**: *immutable static* (fingerprinted JS/CSS/images), *mutable static* (HTML shells, docs), *public API reads* (catalogs, search), *personalized/authenticated*, *write/unsafe methods*. Each class gets its own policy; one global TTL is a smell.
2. **Set `Cache-Control` per class:**
   - Immutable fingerprinted assets: `public, max-age=31536000, immutable` — the URL changes when content changes, so never needs purging.
   - Mutable shared content: `public, max-age=<short>, stale-while-revalidate=<n>, stale-if-error=<n>` — freshness window plus background refresh and graceful origin failure. Use `s-maxage` to set the shared-cache TTL separately from browsers.
   - Personalized responses: `private` (browser only) or `no-store` for sensitive data; **never** let a shared cache store a response that varies by user unless the key includes the user dimension on purpose.
   - Don't rely on heuristic caching: send explicit headers on every cacheable response, including errors you want cached briefly (`404`/`5xx` microcaching, e.g. a few seconds, protects the origin during incidents).
3. **Use validators for revalidation**: `ETag` / `Last-Modified` with conditional requests (`304 Not Modified`) so expired entries cost a header round trip, not a body. Make ETags stable across origin instances (hash of content, not inode/mtime per node).
4. **Design the cache key.** Minimal and explicit: method + normalized URL + only the query params that change the response (drop tracking params like `utm_*`), plus the headers that truly vary (`Accept-Encoding`, `Accept-Language` normalized to supported locales, device class if responses differ). Every `Vary` header or key dimension multiplies entries and lowers the hit ratio; `Vary: Cookie` or `Vary: User-Agent` on a shared cache is usually a mistake — normalize to a few buckets.
5. **Authenticated and personalized content**: split the page into a cacheable shell + personalized fragments/API calls (client-side fetch, edge-side includes, or edge compute); or cache per user/tenant with a key that includes the identity and `private` semantics at the browser. Check that `Authorization` and `Set-Cookie` responses aren't stored by shared caches (`Cache-Control: private`, and strip `Set-Cookie` from cacheable responses).
6. **Invalidation strategy** (in order of preference): (1) versioned/fingerprinted URLs; (2) short TTL + `stale-while-revalidate` for content that tolerates seconds–minutes; (3) tag/surrogate-key purge (`Surrogate-Key`/`Cache-Tag`) on publish events — purge by key, not by wildcard URL; (4) targeted URL purge; (5) full purge only as an emergency. Purge is eventually consistent across POPs and rate-limited by the provider; design for "stale for N seconds" even after a purge, and purge from the write path (event/webhook), not by hand.
7. **Protect the origin**: enable origin shielding / tiered cache (one regional layer collapses misses from many POPs), request collapsing (coalesce simultaneous misses for the same key), connection reuse to origin, and rate-limit or serve-stale during origin failure. Avoid cache-busting query strings from clients that defeat the cache (and are an easy DoS vector).
8. **Compression and transport**: Brotli/gzip at the edge (store both variants keyed by `Accept-Encoding`), HTTP/2/3, TLS 1.3, image optimization/resizing at the edge with a bounded set of variants, range requests for large media.
9. **Measure**: edge hit ratio *by content class* and byte hit ratio, origin offload %, origin requests/s for cacheable paths, p95 TTFB at the edge vs origin, purge latency, and stale-served counts. A low hit ratio is diagnosed by looking at the top missed cache keys (usually query strings, cookies, or `Vary`) before changing TTLs.
10. **Security review**: cache poisoning (unkeyed inputs such as `X-Forwarded-Host` reflected in responses), cache deception (`/account/profile.css` served from cache), and sensitive responses without `private`/`no-store`. Cache only what is safe to serve to another user.

## Output

```text
Edge caching policy: storefront (CloudFront → ALB → app)

Class               Cache-Control                                            Key                         Invalidation
static assets /a/*  public, max-age=31536000, immutable                      URL (fingerprinted)         new URL per build
product pages       public, s-maxage=60, stale-while-revalidate=300,         URL + Accept-Language       tag purge `product:<id>` from the
                    stale-if-error=3600                                      (normalized to 6 locales)   catalog-updated event
catalog API GET     public, s-maxage=30, stale-while-revalidate=120          URL, params {category,page,sort} only    TTL
cart / account      private, no-store                                       n/a (bypass)                n/a
errors 404/5xx      s-maxage=5 (microcache)                                  URL                         TTL
Key hygiene: strip utm_* and gclid; no Vary: Cookie; ETag = content hash.
Origin protection: origin shield on, request collapsing on, serve stale on origin 5xx.
Security: Set-Cookie stripped from cacheable responses; X-Forwarded-Host not reflected; /account/* bypass regardless of extension.
Baseline: hit ratio 41% (assets 98%, product pages 12%) — product pages missed on `?utm_*` and Vary: Cookie [VERIFY: top-missed-keys report].
Target: product-page hit ratio ≥ 80% [TBD: confirm staleness 60 s with merchandising]; origin requests for cacheable paths −70%.
Rollout: shadow headers → canary 5% → full; watch error rate, stale-served, p95 TTFB.
```

## Quality bar

- Every content class has an explicit policy; personalized content is bypassed or keyed on purpose.
- The cache key lists exactly what varies, with tracking params removed and `Vary` limited.
- Invalidation prefers versioned URLs or tag purge, and accepts eventual consistency across POPs.
- Staleness tolerance is a recorded product decision, and success is measured as hit ratio per class plus origin offload.
- Poisoning and deception risks are checked.

## Anti-patterns to avoid

- One TTL for the whole site, or relying on heuristic freshness.
- `Vary: Cookie` / `Vary: User-Agent` on public content; forwarding all cookies/headers/query strings to the origin and keying on them.
- Caching responses that carry `Set-Cookie` or auth-specific data in a shared cache.
- Purging by wildcard on every deploy instead of fingerprinting assets.
- Judging the cache by overall hit ratio while the expensive routes miss.
- Using `no-cache` when you mean `no-store` (the former allows storing with revalidation).
