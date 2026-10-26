# Changelog — polymath-incident

<!-- markdownlint-disable MD024 -->

## [0.11.0]

### Fixed

- `incident-triage`: sev4 vs ticket rule no longer contradicts itself; latent data/security risk counts; security incidents preserve evidence before rollback; status-page posts need comms-lead approval; never invents responder handles.
- `comms-update`: drafts only; example no longer promises an outcome.
- `postmortem-blameless`: contributing factors (not a single root cause), timeline gaps stay visible, stale "once connectors exist" note removed.

## [0.8.0]

Incident craft: triage, blameless postmortem, comms-update; Postmortem/Comms-update templates.

### Skills

- **comms-update** — Draft an incident communication update — plain language, status (investigating/identified/monitoring/resolved), impact, next-update ETA.
- **incident-triage** — Triage an inbound alert or report — classify severity, name the IC, open comms, and decide whether to mitigate or investigate first.
- **postmortem-blameless** — Write a blameless postmortem to docs/postmortems/<incident-id>.md; frontmatter validated by the Postmortem artifact schema.

### Commands

- **/incident-start** — Triage an incident — assess severity, name IC/operator/comms/scribe, open comms; alias for polymath-incident:incident-triage.
- **/postmortem** — Draft a blameless postmortem from incident notes; alias for polymath-incident:postmortem-blameless.
