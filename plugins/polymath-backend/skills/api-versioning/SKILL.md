---
name: api-versioning
description: Plan an API versioning strategy — URL vs header vs media-type versioning, semantic rules, backward-compatible change classification, consumer-driven contracts, deprecation path.
---

# api-versioning

> The cheapest version is the one you never cut. Most changes can be made backward-compatibly; reserve a new version for the breaks you truly can't avoid — and have a way off the old one.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- Evolving a shipped API and deciding whether/how to version a change.
- Standardizing a versioning + deprecation policy across services.
- A workflow invokes `polymath-backend:api-versioning`.

Not this when: you are designing a brand-new endpoint's shape — that is `polymath-backend:api-design-rest`. For the deprecation *notice/timeline* artifact, `polymath-release:deprecation-plan`; for the consumer upgrade doc, `polymath-release:migration-guide`. This skill sets the strategy those execute.

## Inputs

- The change being made and who consumes the API (internal, partners, public).
- Current versioning approach (if any) and the consumers' upgrade agility.

## Procedure

1. **Classify the change first**: *backward-compatible* (add optional field/endpoint, loosen a constraint) vs *breaking* (remove/rename, change type/semantics, tighten validation, change defaults). Adding an enum value is breaking for clients with exhaustive switches or strict deserializers unless the contract already says unknown values must be tolerated — check before calling it additive. Most changes can be made additively — exhaust that before versioning.
2. **Apply the compatibility contract**: additive-only by default; never repurpose a field; tolerant reader on the consumer side. Make the breaking change unnecessary where you can.
3. **Choose the versioning mechanism** (and apply it consistently): URL path (`/v2/…` — visible, cache-friendly, coarse), header/media-type (`Accept: application/vnd.x.v2+json` — clean URLs, finer, less visible), or query param (simplest, weakest). State the choice and scope (whole API vs per-resource).
4. **Semantic versioning of the contract**: major = breaking, minor = additive, patch = fixes; communicate via the chosen mechanism. Avoid a new major for anything additive.
5. **Consumer-driven contracts**: where consumers are known, capture their expectations as contract tests so a change that breaks a real consumer fails CI before release — not in production.
6. **Deprecation path** — required for any breaking version: support old + new in parallel, announce with a timeline + `Deprecation`/`Sunset` headers, track usage to know when it's safe to remove (hand the notice to `polymath-release:deprecation-plan`, the upgrade steps to `migration-guide`).
7. **Don't proliferate versions**: a supported version is a maintenance cost; cap how many you run and drive migration actively.

## Output

```text
API versioning: refunds API — make `reason` required on POST /refunds

Change:        tightening validation (optional → required) = BREAKING
Additive path: keep `reason` optional; default it to "unspecified" server-side; warn via a Deprecation header
               on requests without it → no new version needed now
If breaking anyway:
  Mechanism:   URL path, whole API (/v2) — matches the existing /v1 convention
  Contract:    additive-only within a major; unknown enum values must be tolerated (documented)
  Consumers:   3 partners with Pact contracts → CI fails before release if their requests break
  Parallel:    /v1 + /v2 for 6 months; Deprecation + Sunset headers on /v1 from day one
  Removal:     when /v1 traffic < 1% for 30 days → hand to polymath-release:deprecation-plan
Versions in support after this: 2 (cap: 2)
```

## Quality bar

- The change is classified breaking vs compatible, and additive alternatives are exhausted first.
- One versioning mechanism is chosen and applied consistently.
- Any breaking version ships with a parallel-support window, usage tracking, and a deprecation timeline.
- Known consumers are protected by contract tests.
