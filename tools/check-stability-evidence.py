#!/usr/bin/env python3
"""STABILITY-1: enforce registry/stability-evidence.json against the catalog.

The ledger at registry/stability-evidence.json is the receipt for every
status claim in registry/polymath-catalog.json. A status flip to `stable`
on its own is just a marketing change; the ledger is what proves the
plugin has earned the tier.

This checker enforces:

  1. Ledger validates against
     registry/schemas/stability-evidence.schema.json (when jsonschema is
     installed).
  2. Every plugin in registry/polymath-catalog.json has exactly one ledger
     entry, and vice versa.
  3. target_status is greater-than-or-equal to current catalog status
     on the experimental → beta → stable ladder (deprecated is
     orthogonal and only allowed when current status is deprecated).
  4. Per-status evidence gates:
       - stable: live_bakeoff_run, live_trigger_run, external_user_url,
         promotion_pr, changelog_entry MUST be non-null. For
         integration and infra plugins, distinct_value_url
         MUST also be non-null. evidence_state MUST be `stable` or
         `stable-ready`.
       - beta: evidence_state MUST be `on-disk-skill`,
         `on-disk-foundation`, or `stable-ready`. For
         integration and infra plugins, distinct_value_url
         MUST be non-null (post-Iteration-0 connector/infra policy).
       - experimental: no required fields beyond presence.
       - deprecated: changelog_entry MUST be non-null.
  5. distinct_value_url MUST be null for plugins that are neither
     connector nor infra (it is a field reserved for those categories).

Exit code: 0 if all checks pass, 1 otherwise.

Run as `python3 tools/check-stability-evidence.py`. Wired into
tools/conformance.sh as the STABILITY-1 cross-check.
"""
from __future__ import annotations

import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
CATALOG = REPO / "registry" / "polymath-catalog.json"
LEDGER = REPO / "registry" / "stability-evidence.json"
LEDGER_SCHEMA = REPO / "registry" / "schemas" / "stability-evidence.schema.json"
PLUGINS_DIR = REPO / "plugins"

# experimental < beta < stable; deprecated is off-ladder.
LADDER = {"experimental": 0, "beta": 1, "stable": 2}

EVIDENCE_FOR_BETA = {"on-disk-skill", "on-disk-foundation", "stable-ready", "stable"}
EVIDENCE_FOR_STABLE = {"stable-ready", "stable"}


def is_conn_or_infra(name: str) -> bool:
    # Detect by artifact, not name prefix (concept plugins dropped the
    # connector-/infra- prefix): an integration plugin ships a .mcp.json; an
    # infra plugin carries capability bindings/ but no .mcp.json. Matches the
    # detection used by INTEGRATION-1/2, MCP-PKG, and sync-integration-policy.
    d = PLUGINS_DIR / name
    return (d / ".mcp.json").exists() or (d / "bindings").is_dir()


def main() -> int:
    errors: list[str] = []

    catalog = json.loads(CATALOG.read_text())
    ledger = json.loads(LEDGER.read_text())

    # 1. Schema validation (optional — only if jsonschema is installed).
    try:
        import jsonschema  # type: ignore

        schema = json.loads(LEDGER_SCHEMA.read_text())
        validator = jsonschema.Draft202012Validator(schema)
        for err in sorted(validator.iter_errors(ledger), key=lambda e: list(e.path)):
            errors.append(f"stability-evidence.json schema: {list(err.path)}: {err.message}")
    except ImportError:
        print("note: jsonschema not installed; skipping schema validation", file=sys.stderr)

    catalog_names = set(catalog.get("plugins", {}).keys())
    ledger_names = set(ledger.get("entries", {}).keys())

    # 2. Plugin-set agreement.
    for name in sorted(catalog_names - ledger_names):
        errors.append(f"{name}: in registry/polymath-catalog.json but missing from registry/stability-evidence.json")
    for name in sorted(ledger_names - catalog_names):
        errors.append(f"{name}: in registry/stability-evidence.json but missing from registry/polymath-catalog.json")

    # 3 + 4 + 5. Per-entry checks.
    for name in sorted(catalog_names & ledger_names):
        cur = catalog["plugins"][name].get("status")
        entry = ledger["entries"][name]
        target = entry.get("target_status")
        evidence_state = entry.get("evidence_state")
        conn_or_infra = is_conn_or_infra(name)

        # 3. Target status >= current status.
        if cur == "deprecated":
            if target != "deprecated":
                errors.append(
                    f"{name}: current status is `deprecated` but target_status is "
                    f"`{target}`. Deprecated plugins must keep target_status=deprecated."
                )
        else:
            if target == "deprecated":
                # Allowed only if we're explicitly winding the plugin down.
                # We still expect a changelog_entry in that case.
                if not entry.get("changelog_entry"):
                    errors.append(
                        f"{name}: target_status=deprecated requires a changelog_entry "
                        f"naming the replacement / removal date."
                    )
            elif target not in LADDER:
                errors.append(f"{name}: unknown target_status `{target}`")
            elif cur not in LADDER:
                errors.append(f"{name}: unknown current status `{cur}` in catalog")
            elif LADDER[target] < LADDER[cur]:
                errors.append(
                    f"{name}: target_status `{target}` is below current status `{cur}`. "
                    f"Demotion goes through a CHANGELOG entry, not the ledger."
                )

        # 4. Per-status evidence gates.
        live_bakeoff = entry.get("live_bakeoff_run")
        live_trigger = entry.get("live_trigger_run")
        adopter = entry.get("external_user_url")
        promo_pr = entry.get("promotion_pr")
        changelog = entry.get("changelog_entry")
        distinct = entry.get("distinct_value_url")

        if cur == "stable":
            for field, value in [
                ("live_bakeoff_run", live_bakeoff),
                ("live_trigger_run", live_trigger),
                ("external_user_url", adopter),
                ("promotion_pr", promo_pr),
                ("changelog_entry", changelog),
            ]:
                if not value:
                    errors.append(
                        f"{name}: catalog says `stable` but {field} is null in ledger. "
                        f"Status flip without evidence is not allowed."
                    )
            if conn_or_infra and not distinct:
                errors.append(
                    f"{name}: connector/infra plugin marked `stable` but "
                    f"distinct_value_url is null. Per docs/INTEGRATION-POLICY.md the "
                    f"stable bar requires primary-source evidence that Polymath adds "
                    f"workflow / critique / safety value beyond the official surface."
                )
            if evidence_state not in EVIDENCE_FOR_STABLE:
                errors.append(
                    f"{name}: catalog says `stable` but evidence_state is "
                    f"`{evidence_state}` (expected one of {sorted(EVIDENCE_FOR_STABLE)})."
                )
        elif cur == "beta":
            if evidence_state not in EVIDENCE_FOR_BETA:
                errors.append(
                    f"{name}: catalog says `beta` but evidence_state is "
                    f"`{evidence_state}` (expected one of {sorted(EVIDENCE_FOR_BETA)}). "
                    f"Beta requires closed on-disk evidence."
                )
            if conn_or_infra and not distinct:
                errors.append(
                    f"{name}: connector/infra plugin marked `beta` but "
                    f"distinct_value_url is null. Per docs/INTEGRATION-POLICY.md, "
                    f"promotion above experimental requires primary-source "
                    f"distinct-value evidence."
                )
        elif cur == "deprecated":
            if not changelog:
                errors.append(
                    f"{name}: catalog says `deprecated` but changelog_entry is null. "
                    f"Deprecation must be recorded in CHANGELOG."
                )

        # 5. distinct_value_url is reserved for connector/infra plugins.
        if not conn_or_infra and distinct is not None:
            errors.append(
                f"{name}: distinct_value_url is set on a non-connector / non-infra "
                f"plugin. This field is reserved for integration and infra plugins "
                f"per docs/INTEGRATION-POLICY.md."
            )

    if errors:
        print("check-stability-evidence: FAILED", file=sys.stderr)
        for e in errors:
            print(f"  ✗ {e}", file=sys.stderr)
        return 1

    n = len(catalog_names)
    print(
        f"check-stability-evidence: OK — {n} plugins have evidence ledger entries "
        f"consistent with registry/polymath-catalog.json"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
