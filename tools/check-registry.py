#!/usr/bin/env python3
"""Registry cross-checks — one subcommand per conformance rule.

  check-registry.py catalog      MANIFEST-3 cross-check
  check-registry.py profiles     PROFILE-1
  check-registry.py stability    STABILITY-1

catalog — cross-file consistency for the Polymath catalog. Verifies that
.claude-plugin/marketplace.json, every plugin's .claude-plugin/plugin.json,
and registry/polymath-catalog.json all agree on the plugin set and on
per-plugin versions. Also validates the catalog file against
registry/schemas/polymath-catalog.schema.json when jsonschema is installed.
Failure modes this catches that `claude plugin validate --strict` would miss
when the Claude CLI is not on PATH (i.e. in CI without the CLI installed):

  - Plugin listed in marketplace.json but missing from polymath-catalog.json
  - Plugin listed in polymath-catalog.json but missing from marketplace.json
  - marketplace.json entry version != plugin.json version

profiles — validate registry/polymath-profiles.json against the marketplace.
Install profiles (role spines) only help discovery if they never name a
plugin that does not exist. Asserts:

  1. Every plugin listed in any profile (and in `_spine`) is present in
     .claude-plugin/marketplace.json.
  2. No profile redundantly lists a `_spine` plugin (the spine is implicit).
  3. Each profile has a non-empty `title`, `for`, and `plugins`.

Drift-guard so a fold/rename that removes a plugin can't silently leave a
dangling profile reference.

stability — enforce registry/stability-evidence.json against the catalog.
The ledger is the receipt for every status claim in
registry/polymath-catalog.json: a status flip to `stable` on its own is just
a marketing change; the ledger is what proves the plugin has earned the
tier. Enforces:

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

All three are wired into tools/conformance.sh --all. Exit code per
subcommand: 0 if all checks pass, 1 otherwise.
"""
from __future__ import annotations

import argparse
import json
import sys

from lib.repo import load_catalog, load_marketplace, plugins_dir, repo_root

ROOT = repo_root()
PLUGINS_DIR = plugins_dir()
CATALOG_SCHEMA = ROOT / "registry" / "schemas" / "polymath-catalog.schema.json"
PROFILES = ROOT / "registry" / "polymath-profiles.json"
LEDGER = ROOT / "registry" / "stability-evidence.json"
LEDGER_SCHEMA = ROOT / "registry" / "schemas" / "stability-evidence.schema.json"


def _schema_errors(instance: dict, schema_path, label: str) -> list[str]:
    """Validate `instance` against the JSON Schema at `schema_path` when
    jsonschema is installed; otherwise note the skip on stderr."""
    try:
        import jsonschema  # type: ignore
    except ImportError:
        print("note: jsonschema not installed; skipping schema validation", file=sys.stderr)
        return []
    schema = json.loads(schema_path.read_text())
    validator = jsonschema.Draft202012Validator(schema)
    return [
        f"{label} schema: {list(err.path)}: {err.message}"
        for err in sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
    ]


# ---------------------------------------------------------------------------
# catalog — MANIFEST-3 cross-check
# ---------------------------------------------------------------------------


def catalog_check() -> int:
    errors: list[str] = []

    marketplace = load_marketplace()
    catalog = load_catalog()

    # 1. JSON Schema validation (optional — only if jsonschema is installed).
    errors.extend(_schema_errors(catalog, CATALOG_SCHEMA, "polymath-catalog.json"))

    # 2. Plugin-set agreement.
    marketplace_names = {p["name"] for p in marketplace.get("plugins", [])}
    catalog_names = set(catalog.get("plugins", {}).keys())

    only_in_marketplace = marketplace_names - catalog_names
    only_in_catalog = catalog_names - marketplace_names
    for name in sorted(only_in_marketplace):
        errors.append(f"{name}: listed in marketplace.json but missing from polymath-catalog.json")
    for name in sorted(only_in_catalog):
        errors.append(f"{name}: listed in polymath-catalog.json but missing from marketplace.json")

    # 3. Version agreement between marketplace entry and plugin.json.
    for entry in marketplace.get("plugins", []):
        name = entry["name"]
        market_version = entry.get("version")
        plugin_json = PLUGINS_DIR / name / ".claude-plugin" / "plugin.json"
        if not plugin_json.exists():
            errors.append(f"{name}: plugin.json not found at {plugin_json.relative_to(ROOT)}")
            continue
        try:
            plugin_data = json.loads(plugin_json.read_text())
        except json.JSONDecodeError as e:
            errors.append(f"{name}: plugin.json is not valid JSON: {e}")
            continue
        plugin_version = plugin_data.get("version")
        if market_version != plugin_version:
            errors.append(
                f"{name}: version drift — marketplace.json says {market_version!r}, "
                f"plugin.json says {plugin_version!r}. At install time plugin.json wins "
                f"(calculatePluginVersion precedence). Update the marketplace entry."
            )

    if errors:
        print("check-catalog: FAILED", file=sys.stderr)
        for e in errors:
            print(f"  ✗ {e}", file=sys.stderr)
        return 1

    print(f"check-catalog: OK — {len(marketplace_names)} plugins agree across "
          f"marketplace.json, every plugin.json, and polymath-catalog.json")
    return 0


# ---------------------------------------------------------------------------
# profiles — PROFILE-1
# ---------------------------------------------------------------------------


def profiles_check() -> int:
    if not PROFILES.exists():
        print("check-profiles: no registry/polymath-profiles.json (skipped)")
        return 0
    market = {p["name"] for p in load_marketplace()["plugins"]}
    doc = json.loads(PROFILES.read_text())
    spine = set(doc.get("_spine", []))
    profiles = doc.get("profiles", {})

    errors: list[str] = []

    for p in spine:
        if p not in market:
            errors.append(f"_spine names unknown plugin: {p}")

    for name, prof in profiles.items():
        for field in ("title", "for", "plugins"):
            if not prof.get(field):
                errors.append(f"profile {name!r}: missing/empty `{field}`")
        for p in prof.get("plugins", []):
            if p not in market:
                errors.append(f"profile {name!r}: unknown plugin {p!r}")
            if p in spine:
                errors.append(f"profile {name!r}: redundantly lists spine plugin {p!r}")

    for e in errors:
        print(f"  FAIL  {e}")
    if errors:
        print(f"check-profiles: FAILED ({len(errors)} error(s))")
        return 1
    print(f"check-profiles: OK — {len(profiles)} profile(s), all plugins resolve against the marketplace")
    return 0


# ---------------------------------------------------------------------------
# stability — STABILITY-1
# ---------------------------------------------------------------------------

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


def stability_check() -> int:
    errors: list[str] = []

    catalog = load_catalog()
    ledger = json.loads(LEDGER.read_text())

    # 1. Schema validation (optional — only if jsonschema is installed).
    errors.extend(_schema_errors(ledger, LEDGER_SCHEMA, "stability-evidence.json"))

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


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Registry cross-checks — one subcommand per conformance rule."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser(
        "catalog",
        help="marketplace.json / plugin.json / polymath-catalog.json agreement (MANIFEST-3)",
    )
    sub.add_parser(
        "profiles",
        help="polymath-profiles.json plugins resolve against the marketplace (PROFILE-1)",
    )
    sub.add_parser(
        "stability",
        help="stability-evidence.json backs every catalog status claim (STABILITY-1)",
    )

    args = parser.parse_args()
    if args.cmd == "catalog":
        return catalog_check()
    if args.cmd == "profiles":
        return profiles_check()
    if args.cmd == "stability":
        return stability_check()
    raise AssertionError(args.cmd)


if __name__ == "__main__":
    raise SystemExit(main())
