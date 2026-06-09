#!/usr/bin/env python3
"""MCP-PKG gate: every connector .mcp.json package is verified or disclosed.

Several integration plugins reference an MCP server package in
their `.mcp.json` `npx` command. Some of those packages are published on
npm and resolve on `npx -y <pkg>`; others are placeholder names for a
vendor's MCP server that does not (yet) ship as that npm package — it may be
a hosted remote URL, a Go binary, a Python `uvx` package, or a CLI
subcommand. A placeholder that resolves to nothing makes the connector
dead-on-install: `npx -y @vendor/mcp-server` fails to download and the MCP
server never starts.

This gate makes that state explicit and drift-proof. It does NOT hit the
network (so CI stays hermetic). Instead it classifies every referenced
package against two in-script registries and enforces:

  - VERIFIED   — confirmed to resolve on npm. No disclosure required.
  - UNVERIFIED — confirmed NOT to resolve on npm (placeholder). The owning
                 connector's README MUST carry the disclosure marker
                 (DISCLOSURE_MARKER) so an installing user is warned.
  - neither    — FAIL. A new connector, or a renamed package, must be
                 consciously classified here rather than silently shipping
                 an unverifiable command.

Run `--online` (maintainer-only; needs network) to re-check the registries
against npm and report any classification that has gone stale.

Verified against npm on 2026-06-08.

Usage:
  tools/check-mcp-packages.py            # offline gate (CI)
  tools/check-mcp-packages.py --online   # refresh classification vs npm
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
PLUGINS_DIR = REPO / "plugins"

DISCLOSURE_MARKER = "<!-- mcp-package-status -->"

# Packages confirmed to resolve on npm (npx -y <pkg> downloads a real package).
VERIFIED = {
    "@modelcontextprotocol/server-github",
    "@modelcontextprotocol/server-slack",
    "@sentry/mcp-server",
}

# Placeholder package names that do NOT resolve on npm as of the date above.
# The vendor's MCP server may exist under a different distribution (hosted
# URL, Go binary, uvx, CLI subcommand). The owning connector must disclose
# this in its README. Move a package up to VERIFIED only after confirming
# `npm view <pkg> version` returns a version.
UNVERIFIED = {
    "@datadog/mcp-server",
    "@grafana/mcp-server",
    "@honeycomb/mcp-server",
    "@elastic/mcp-server",
    "@pagerduty/mcp-server",
    "@snyk/mcp-server",
    "@statuspage/mcp-server",
    "@modelcontextprotocol/server-atlassian",
    "@linear/mcp-server",
}


def package_from_args(args: list[str]) -> str | None:
    """Extract the npm package an `npx` invocation installs.

    npx args look like ["-y", "@scope/pkg", ...maybe more]. The package is
    the first arg that is not a flag (does not start with '-').
    """
    for tok in args:
        if tok.startswith("-"):
            continue
        return tok
    return None


def connector_dirs() -> list[pathlib.Path]:
    # Detect connectors by the artifact that matters here — a .mcp.json — rather
    # than a name prefix, so the gate survives concept-plugin renames (vcs, chat,
    # paging, …) and the observability merge.
    return sorted(
        p for p in PLUGINS_DIR.iterdir()
        if p.is_dir() and (p / ".mcp.json").exists()
    )


def npm_resolves(pkg: str) -> bool:
    try:
        out = subprocess.run(
            ["npm", "view", pkg, "version"],
            capture_output=True, text=True, timeout=60,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return out.returncode == 0 and bool(out.stdout.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--online", action="store_true",
                        help="Re-check the registries against npm (needs network).")
    args = parser.parse_args()

    problems: list[str] = []
    # Collect (package, connector_name) references across every connector.
    refs: list[tuple[str, str, pathlib.Path]] = []
    for cdir in connector_dirs():
        mcp = cdir / ".mcp.json"
        if not mcp.exists():
            continue  # not an MCP plugin (no .mcp.json) — nothing for MCP-PKG to check.
        data = json.loads(mcp.read_text())
        for server, spec in data.get("mcpServers", {}).items():
            command = spec.get("command", "")
            pkg = package_from_args(spec.get("args", [])) if command == "npx" else command
            if not pkg:
                problems.append(f"{cdir.name}: server '{server}' has no resolvable command/package")
                continue
            refs.append((pkg, cdir.name, cdir))

    if args.online:
        # Maintainer refresh: report registry rows that disagree with npm.
        checked: dict[str, bool] = {}
        for pkg, _name, _dir in refs:
            if pkg not in checked:
                checked[pkg] = npm_resolves(pkg)
        for pkg, resolves in sorted(checked.items()):
            classified = "VERIFIED" if pkg in VERIFIED else "UNVERIFIED" if pkg in UNVERIFIED else "UNCLASSIFIED"
            actual = "resolves" if resolves else "missing"
            flag = ""
            if resolves and pkg in UNVERIFIED:
                flag = "  <-- now resolves; promote to VERIFIED"
            elif not resolves and pkg in VERIFIED:
                flag = "  <-- no longer resolves; demote to UNVERIFIED"
            print(f"  {classified:13} {actual:9} {pkg}{flag}")

    # Offline gate (always runs).
    for pkg, name, cdir in refs:
        if pkg in VERIFIED:
            continue
        if pkg in UNVERIFIED:
            readme = cdir / "README.md"
            if not readme.exists() or DISCLOSURE_MARKER not in readme.read_text():
                problems.append(
                    f"{name}: uses unverified MCP package '{pkg}' but README has no "
                    f"disclosure marker ({DISCLOSURE_MARKER})"
                )
            continue
        problems.append(
            f"{name}: MCP package '{pkg}' is unclassified — add it to VERIFIED or "
            f"UNVERIFIED in tools/check-mcp-packages.py (verify with: npm view {pkg} version)"
        )

    if problems:
        for p in problems:
            print(f"  ✗ MCP-PKG: {p}", file=sys.stderr)
        print(f"\ncheck-mcp-packages: {len(problems)} problem(s)", file=sys.stderr)
        return 1

    n_unverified = sum(1 for pkg, _, _ in refs if pkg in UNVERIFIED)
    print(
        f"check-mcp-packages: {len(refs)} MCP package reference(s) across "
        f"{len(connector_dirs())} connector(s) — all verified or disclosed "
        f"({n_unverified} disclosed-unverified)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
