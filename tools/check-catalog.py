#!/usr/bin/env python3
"""Cross-file consistency check for the Polymath catalog.

Verifies that .claude-plugin/marketplace.json, every plugin's
.claude-plugin/plugin.json, and shared/polymath-catalog.json all agree
on the plugin set and on per-plugin versions. Also validates the
catalog file against shared/schemas/polymath-catalog.schema.json when
jsonschema is installed.

Failure modes this catches that `claude plugin validate --strict`
would miss when the Claude CLI is not on PATH (i.e. in CI without the
CLI installed):

  - Plugin listed in marketplace.json but missing from polymath-catalog.json
  - Plugin listed in polymath-catalog.json but missing from marketplace.json
  - marketplace.json entry version != plugin.json version

Exit code: 0 if all checks pass, 1 otherwise.
"""
from __future__ import annotations

import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
MARKETPLACE = REPO / ".claude-plugin" / "marketplace.json"
CATALOG = REPO / "shared" / "polymath-catalog.json"
CATALOG_SCHEMA = REPO / "shared" / "schemas" / "polymath-catalog.schema.json"
PLUGINS_DIR = REPO / "plugins"


def main() -> int:
    errors: list[str] = []

    marketplace = json.loads(MARKETPLACE.read_text())
    catalog = json.loads(CATALOG.read_text())

    # 1. JSON Schema validation (optional — only if jsonschema is installed).
    try:
        import jsonschema  # type: ignore
        schema = json.loads(CATALOG_SCHEMA.read_text())
        validator = jsonschema.Draft202012Validator(schema)
        for err in sorted(validator.iter_errors(catalog), key=lambda e: list(e.path)):
            errors.append(f"polymath-catalog.json schema: {list(err.path)}: {err.message}")
    except ImportError:
        print("note: jsonschema not installed; skipping schema validation", file=sys.stderr)

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
            errors.append(f"{name}: plugin.json not found at {plugin_json.relative_to(REPO)}")
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


if __name__ == "__main__":
    sys.exit(main())
