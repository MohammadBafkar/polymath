---
artifact: Advisory
schemaVersion: 0.1
title: "{{title}}"
advisory_id: "{{advisory_id}}"
severity: "{{severity}}"
classification: "{{classification}}"
affected_versions: "{{affected_versions}}"
fixed_versions: "{{fixed_versions}}"
published: "{{date}}"
---

# {{advisory_id}}: {{title}}

> Security or breaking-change advisory. Plain language, action first. Tone
> is informative + calm, not alarming.

## Severity

`{{severity}}` (Critical / High / Medium / Low). Mapped from impact + exploitability for security; or breaking-impact level for breaking-change advisories.

## Classification

`{{classification}}` — one of:
- **Security**: vulnerability with CVE-style impact.
- **Breaking change**: API / behavior incompatibility that requires caller changes.
- **Data integrity**: corruption / loss / disclosure risk.
- **Compliance**: regulatory requirement change.

## Affected versions

`{{affected_versions}}` — exact version ranges (e.g. `≥ 1.4.0, < 1.6.3`). No "all old versions".

## Fixed versions

`{{fixed_versions}}` — exact versions to upgrade to (e.g. `1.6.3`, `1.5.7-patch.2`).

## Action required

Bulleted, in priority order. The reader scans this section first.

- [ ] Upgrade to `{{fixed_versions}}` (recommended).
- [ ] If upgrade isn't possible, apply the workaround below.
- [ ] Verify the verification step (see below).

## Workaround

If you can't upgrade immediately, the workaround:

```text
<concrete steps; configuration / firewall rule / etc.>
```

Cite the trade-off the workaround makes vs. the upgrade. Workarounds expire — set an expiration date.

## Verification

How to confirm you're protected after the upgrade or workaround.

```text
<command / query / health check>
# Expected output: …
```

## Technical detail (for security advisories)

For security: vulnerability class (e.g. SQLi, IDOR, RCE), reachability,
attack prerequisites. CWE if applicable.

For breaking change: what changed, in what code path.

## Credit / acknowledgements

For security: name the reporter (with their permission). "Reported responsibly by <name>" — credit is the right thing.

## Timeline

- `<date>`: reported / discovered.
- `<date>`: fix shipped in `{{fixed_versions}}`.
- `<date>`: advisory published.

(Coordinated disclosure timeline if applicable.)

## References

- CVE: <id> (security only).
- Migration guide / patch notes.
- Underlying PR.
