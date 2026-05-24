---
name: metrics-design
description: Design service metrics using RED (services) and USE (resources) — name, type, labels, cardinality budget; the smallest set that supports the SLO.
---

# metrics-design

> Pin RED metrics for services and USE metrics for resources. Output is a labeled metric list with a cardinality budget.

## When to use

- A new service needs metrics before going live.
- An existing service has a hundred metrics and no one knows which to alert on.

## The two methods

- **RED** (Tom Wilkie) — for services:
  - **R**ate — requests per second.
  - **E**rrors — error rate (and per error class).
  - **D**uration — latency distribution.
- **USE** (Brendan Gregg) — for resources:
  - **U**tilization — % busy.
  - **S**aturation — queue depth or wait time.
  - **E**rrors — counter of unrecoverable errors per resource.

Most services need RED for themselves and USE for the resources they depend on (DB, queue, cache).

## Procedure

1. **Per service endpoint or job**: define RED.
   - `http_requests_total{route, method, status}` — counter.
   - `http_request_duration_seconds{route, method}` — histogram.
   - `errors_total{route, kind}` — counter (`kind` = validation / upstream / internal).
2. **Per resource the service uses**: define USE.
   - DB pool: `db_pool_in_use`, `db_pool_wait_seconds`, `db_errors_total`.
   - Queue: `queue_depth`, `queue_enqueue_wait_seconds`, `queue_errors_total`.
   - Cache: `cache_hit_ratio`, `cache_errors_total`.
3. **Cardinality budget** — count the labels' Cartesian product.
   - `route` (~20) × `method` (~5) × `status` (~10) = 1,000 series per metric. Fine.
   - `user_id` on a request counter — millions of series. Don't.
   - Set a budget per service (e.g. 50,000 active series) and enforce it via PromQL `count by (__name__)` checks.
4. **Histograms not summaries** for latency. Histograms aggregate across instances; summaries don't.
   - Bucket choice: a geometric series matching the SLO threshold. For "P99 < 500ms" pick `[5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000]` ms.
5. **Naming** — match Prometheus conventions: `<thing>_<unit>_total` for counters with units, `<thing>_seconds` for time, no upper-case, no spaces.
6. **Pull vs push** — Prometheus default is pull (scrape). For short-lived jobs use Pushgateway or OTel push.
7. **SLI mapping** — name which metrics power each SLO directly. Anything not powering an SLO or operational dashboard is a candidate for deletion.

## Output

```text
Metrics design: refund-service

RED (service):
  http_requests_total{route, method, status}                    counter
  http_request_duration_seconds{route, method}                  histogram
    buckets: 5,10,25,50,100,250,500,1000,2500,5000 ms
  errors_total{route, kind}                                     counter
    kind ∈ { validation, upstream, internal }

USE (resources):
  db_pool_in_use                                                gauge
  db_pool_wait_seconds                                          histogram (buckets 1,5,10,50,100 ms)
  db_errors_total                                               counter
  stripe_client_errors_total{kind}                              counter
  stripe_client_request_duration_seconds                        histogram

Cardinality budget:
  ~5,000 active series. Reviewed monthly.
  Forbidden labels: user_id, request_id, order_id (high cardinality).

SLI mapping:
  refund-latency SLO → http_request_duration_seconds{route="/refunds"}
  refund-availability SLO → http_requests_total{route="/refunds",status="5xx"}
                            / http_requests_total{route="/refunds"}

Anti-cardinality guard:
  CI rule: any new metric introducing a forbidden label fails the PR.
```

## Anti-patterns to avoid

- One giant metric `everything_total{thing,subthing,subsubthing}` — cardinality bomb.
- Summaries for latency.
- "Request count by user_id" — that's analytics, not metrics.
- Hundreds of metrics with no SLI mapping.
