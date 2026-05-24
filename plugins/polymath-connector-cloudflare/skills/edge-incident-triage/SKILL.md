---
name: edge-incident-triage
description: Triage a Cloudflare edge incident — separates origin failure from edge failure from WAF rule from DNS misconfiguration with HTTP-status + WAF-event evidence.
---

# edge-incident-triage

> Given a domain + symptom, identify which layer is responsible: origin, edge cache, Workers, WAF, or DNS. Output is a layer-classified diagnosis with the supporting evidence and an explicit remediation hint.

## When to use

- A site is throwing 5xx and the root cause could be edge or origin.
- A subset of users (e.g. one country) gets blocked while others don't — almost always WAF or geo-routing.
- A `respondToIncident` flow needs to know which side to call.

## Inputs

- Domain or zone (required) — `refund.example.com` or zone ID (`<32-char hex>`).
- Symptom (required) — short description: "intermittent 502s", "TLS handshake failures", "blocked in EU", etc.
- Time window (optional) — defaults to last 30 minutes.

## Procedure

1. **Resolve the zone.** `zones.list?name=<domain>` → zone ID. If multiple match (apex + subzone), surface and pick the most specific.
2. **HTTP status histogram.** `analytics.dashboard` or GraphQL Analytics: count of 2xx / 3xx / 4xx / 5xx in the window. Bucket by edge response source (`edge`, `worker`, `origin`).
3. **Origin health.** GraphQL `httpRequestsAdaptiveGroups` filtered to `originResponseStatus`. If origin 5xx ≫ edge 5xx, the problem is origin — surface upstream IP + Cloudflare-CF-Ray for grep.
4. **Edge / Workers errors.** If `worker_status >= 500` or `cacheStatus` is dominated by `bypass` or `expired`, the problem is at the edge. Pull Worker logs via `tailDeployment` (limited window) or Workers Analytics.
5. **WAF events.** `firewallEventsAdaptive` or `securityEvents`. Group by `ruleId` and `country`. A spike in a single rule + country tuple is the answer.
6. **DNS sanity.** `dns_records.list` for the apex/host. Verify A/AAAA/CNAME match the expected origin; flag any `proxied=false` records (Cloudflare not in front, so no CDN/WAF coverage).
7. **Classify** as one of:
   - **origin-failure** — origin 5xx dominant.
   - **edge-failure** — Workers exceptions or cache failures dominant.
   - **waf-block** — firewall events spike, ruleId identified.
   - **dns-misconfig** — record points elsewhere, or `proxied=false` on a record that should be proxied.
   - **mixed** — multiple layers degraded; needs human triage.

## Output

```text
edge-incident-triage

Zone:     refund.example.com (zone id ab12...)
Window:   last 30 minutes
Symptom:  intermittent 502s

HTTP status histogram (edge)
  2xx: 88,402   4xx: 1,910   5xx: 9,033 (8.9%)

Bucket by response source
  origin:     5xx = 8,901   ← dominant
  worker:     5xx = 22
  cf-edge:    5xx = 110

Origin response codes (proxied)
  origin 502: 8,402   origin 504: 481   origin 500: 18

Workers tail (window)
  worker 'refund-edge'  request errors: 22  (no spike)

WAF events
  no rule contributes > 50 events in the window.

DNS sanity
  refund.example.com  CNAME → refund-origin.example.com  proxied=true (correct)

Classification: ORIGIN-FAILURE
  Reason: 8,901 origin 5xx ≫ 132 edge 5xx; WAF + DNS clean.

Hint: open the origin app's runtime logs; CF-Ray on a sample failure is
      `7a8b9c0d1e2f3a4b`. Filter origin logs by that ray ID for the precise request.
```

## Quality bar

- Status histogram surfaced before classification.
- Bucketed by response source (origin / worker / edge); a single-bucket count is not enough.
- WAF + DNS sanity at least checked, even when origin looks obviously broken (rules out compound failures).
- Classification matches evidence; "mixed" is a valid answer when no single layer dominates.

## Anti-patterns to avoid

- Calling it "edge failure" because Cloudflare is in the request path. Cloudflare is the messenger most of the time; the histogram is the proof.
- Skipping the DNS check when the symptom looks like a 5xx. Sometimes the record was unproxied at midnight and traffic is bypassing the CDN entirely.
- Investigating WAF "just in case" with no event spike. The WAF data is loud; lean on it only when a rule × country tuple is anomalous.
- Treating a single CF-Ray as representative. Pull at least 5-10 sample rays before concluding.
