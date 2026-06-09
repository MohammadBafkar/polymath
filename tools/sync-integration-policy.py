#!/usr/bin/env python3
"""Sync the INTEGRATION-POLICY § 1 disclosure block into every
integration & infra plugin README.

Single source of truth: the two markdown tables in
docs/INTEGRATION-POLICY.md (§ 3.1 and § 3.2). The status field comes
from registry/polymath-catalog.json so demote/promote stays in sync.

Modes:
  --check   Exit 1 if any in-scope README's policy block diverges
            from what would be regenerated. Used by
            tools/conformance.sh INTEGRATION-2.
  --update  Insert / rewrite the policy block in every in-scope
            README. Safe to re-run.

Block markers (idempotent):
  <!-- integration-policy:start -->
  ...
  <!-- integration-policy:end -->
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
POLICY = REPO / "docs" / "INTEGRATION-POLICY.md"
CATALOG = REPO / "registry" / "polymath-catalog.json"
PLUGINS_DIR = REPO / "plugins"

START_MARKER = "<!-- integration-policy:start -->"
END_MARKER = "<!-- integration-policy:end -->"


def parse_policy_tables() -> dict[str, dict[str, str]]:
    """Return {plugin_name: {official_surface, polymath_value, sunset_trigger}}."""
    text = POLICY.read_text()
    rows: dict[str, dict[str, str]] = {}
    # Match markdown table rows that start with `| `\`plugin-name\``. Any
    # polymath-* plugin name (concept plugins dropped the connector-/infra-
    # prefix); only the §3.x disclosure tables use this 4-column row shape.
    pattern = re.compile(
        r"^\|\s*`(polymath-[a-z0-9-]+)`\s*\|"
        r"\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$",
        re.MULTILINE,
    )
    for m in pattern.finditer(text):
        name, official, value, sunset = m.group(1), m.group(2), m.group(3), m.group(4)
        rows[name] = {
            "official_surface": official.strip(),
            "polymath_value": value.strip(),
            "sunset_trigger": sunset.strip(),
        }
    return rows


def load_statuses() -> dict[str, str]:
    data = json.loads(CATALOG.read_text())
    return {name: entry.get("status", "unknown") for name, entry in data.get("plugins", {}).items()}


def render_block(name: str, row: dict[str, str], status: str) -> str:
    return (
        f"{START_MARKER}\n"
        f"## Integration policy disclosure\n"
        f"\n"
        f"Auto-generated from [`docs/INTEGRATION-POLICY.md`](../../docs/INTEGRATION-POLICY.md)\n"
        f"by `tools/sync-integration-policy.py`. Do not edit by hand —\n"
        f"edit the policy table and re-run the script.\n"
        f"\n"
        f"- **Official surface:** {row['official_surface']}\n"
        f"- **Polymath value:** {row['polymath_value']}\n"
        f"- **Sunset trigger:** {row['sunset_trigger']}\n"
        f"- **Status:** `{status}`\n"
        f"{END_MARKER}"
    )


def inject_or_replace(readme: pathlib.Path, block: str) -> str:
    text = readme.read_text()
    if START_MARKER in text and END_MARKER in text:
        # Replace existing block, preserving surrounding whitespace.
        pattern = re.compile(
            re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
            re.DOTALL,
        )
        return pattern.sub(block, text, count=1)
    # Insert before the License section if present, else at the end.
    if "\n## License" in text:
        return text.replace("\n## License", f"\n{block}\n\n## License", 1)
    if text.endswith("\n"):
        return text + "\n" + block + "\n"
    return text + "\n\n" + block + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="Exit 1 on divergence.")
    group.add_argument("--update", action="store_true", help="Rewrite blocks.")
    args = parser.parse_args()

    rows = parse_policy_tables()
    statuses = load_statuses()

    # In-scope = every integration/infra plugin on disk, detected by artifact
    # rather than name prefix (so concept-plugin renames + the observability
    # merge stay covered): an integration plugin ships a .mcp.json or bindings/;
    # an infra plugin declares the `infra` keyword. Cross-check against the table.
    def _is_in_scope(p: pathlib.Path) -> bool:
        # MCP connector (.mcp.json) or capability-binding/infra plugin (bindings/).
        return (p / ".mcp.json").exists() or (p / "bindings").is_dir()

    in_scope = sorted(
        p.name for p in PLUGINS_DIR.iterdir()
        if p.is_dir() and _is_in_scope(p)
    )
    missing_from_policy = [n for n in in_scope if n not in rows]
    if missing_from_policy:
        print(
            "ERROR: in-scope plugins missing from docs/INTEGRATION-POLICY.md table:",
            file=sys.stderr,
        )
        for n in missing_from_policy:
            print(f"  - {n}", file=sys.stderr)
        return 2

    diverged: list[str] = []
    updated: list[str] = []
    for name in in_scope:
        row = rows[name]
        status = statuses.get(name, "unknown")
        block = render_block(name, row, status)
        readme = PLUGINS_DIR / name / "README.md"
        if not readme.exists():
            print(f"ERROR: {readme} missing", file=sys.stderr)
            return 2
        new_text = inject_or_replace(readme, block)
        if new_text != readme.read_text():
            if args.check:
                diverged.append(name)
            else:
                readme.write_text(new_text)
                updated.append(name)

    if args.check:
        if diverged:
            print("integration-policy: divergent READMEs (re-run with --update):", file=sys.stderr)
            for n in diverged:
                print(f"  ✗ plugins/{n}/README.md", file=sys.stderr)
            return 1
        print(f"integration-policy: {len(in_scope)} in-scope READMEs in sync")
        return 0

    print(f"integration-policy: updated {len(updated)} README(s); {len(in_scope) - len(updated)} already in sync")
    for n in updated:
        print(f"  ✓ plugins/{n}/README.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
