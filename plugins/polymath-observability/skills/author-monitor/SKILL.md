---
name: author-monitor
description: Author a Datadog monitor — query, threshold, evaluation window, no-data behavior, notification routing; pair with polymath-sre:slo-design for SLO burn-rate monitors.
---

# author-monitor

> Write one Datadog monitor and create it via the MCP server. Output is the monitor JSON + the rationale.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

> **MCP binding (read before any tool call):** if your host has a `datadog` MCP server, use its tools for this skill's data access. Check your own tool list — it may be registered under another name (a Claude Code connector appears as `mcp__claude_ai_<Name>__*`). Tool names differ between servers: use the closest match, and say so when the server is read-only. Never install or start a second copy. If there is none, work without MCP tool calls (give the user the queries or steps to run) and ask before suggesting an install.

## When to use

- A new service needs alerting before going live.
- An existing alert is too noisy or too quiet; we want to tune it.

## Inputs

- The metric or log query.
- The SLO target (if pair with `polymath-sre:slo-design`).
- The destination (Slack channel, PagerDuty service, email list).

## Procedure

If the host's Datadog server is read-only (no create tool — the default for the hosted server), do steps 1-8, validate, then output the monitor JSON for the user to apply instead of creating it. Say so up front. When a create tool exists, still show the final JSON and get explicit approval before creating — a new monitor can page people at 3am.

1. **Decide the monitor type**:
   - **metric alert** — Prometheus/Datadog metric exceeds a threshold.
   - **anomaly** — significant deviation from history. Use only when threshold-based is genuinely impossible.
   - **log alert** — count of matching log lines.
   - **service check** — uptime / synthetic.
   - **composite** — `(monitorA && monitorB) || monitorC`.
   - **SLO burn rate** (`slo alert`) — alerts on how fast an SLO's error budget is burning; the right type for SLO paging (see `polymath-sre:slo-design` for the windows).
2. **Query** — write the metric or log query using metric names you have confirmed exist (search/list metrics first; never guess a name). Validate it before automating; the MCP creates monitors but it doesn't validate semantics. If the server offers a validation tool (`validate_monitor_definition`), run it on the finished definition.
3. **Threshold** — derive from the SLO or from a documented baseline. **Never** "pick a round number that looks right".
4. **Evaluation window** — match the response expectation:
   - Page (sev2): 5-15 min window with a short critical threshold.
   - Ticket: 6h+ window.
5. **No-data behavior** — explicit. For revenue-impacting paths: `notify_no_data: true`, `no_data_timeframe: 10`. For things that legitimately go quiet (low traffic at night): `notify_no_data: false` with a comment explaining why.
6. **Notification message** — Markdown, with sections: what's broken, why it matters, link to runbook, link to dashboard. Use `{{value}}` and `{{#is_alert}}` Datadog template syntax.
7. **Routing** — `@pagerduty-<service>` for pages; `@slack-<channel>` for tickets. Tag the team owner.
8. **Tags** — `team:`, `service:`, `severity:`, `slo:` so monitors can be filtered.

## Output

```text
Monitor: refund-p99-500ms

Type: metric alert
Query: avg(last_5m):p99:trace.http.request{service:refund-service} > 0.5

Thresholds:
  critical: 0.5     (500ms, matches SLO threshold)
  warning:  0.4

Evaluation window: 5 minutes (fast symptom alert; the SLO burn-rate pages
live in separate `slo alert` monitors).

No-data: notify_no_data=true, no_data_timeframe=10 (refund is a hot path).

Message:
  @pagerduty-payments
  ## Refund p99 latency above SLO
  p99 latency on refund-service is {{value}}s (threshold 0.5s, the
  latency SLO's target). Check the SLO burn-rate monitor for budget impact.

  Runbook: <link>
  Dashboard: <link>

Tags: team:payments, service:refund-service, severity:sev2, slo:refund-latency
```

## Quality bar

- Threshold derived from an SLO or a baseline number, with the source named.
- Nothing created without approval of the final JSON.
- `notify_no_data` explicitly set, not defaulted.
- Notification routes via `@pagerduty-<service>` (not a person), tagged with team owner.
- Runbook + dashboard links in the message.

## Anti-patterns to avoid

- Anomaly monitors as the first alert — usually too noisy without a strong baseline.
- "Composite" monitors that fan out across teams. Pick a clear owner.
- Notification messages that contain the threshold as a literal but no link to context.

