#!/usr/bin/env python3
"""Build the MCP availability map for the current session and merge it into
the project-context snapshot.

Invoked by polymath-core's SessionStart hook (after load-project-context.py).
It detects which host agent is running (in-session env markers), scans ONLY
that host's MCP config (tools/mcp-registry.py), resolves every kind=mcp
binding's provider against the project `mcp:` policy, and writes the
resolution into project-context.json under `mcpResolution`:

  {
    "policy": "reuse-host",
    "detectedHost": "opencode",
    "providers": {
      "datadog": {
        "capability": "observability",
        "plugin": "polymath-observability",
        "source": "host",                  # host | plugin | none
        "server": "datadog",               # the server name to reference
        "toolPrefix": "datadog_",          # this host's tool naming
        "host": "opencode", "scope": "user", "matchSignal": "name"
      },
      ...
    }
  }

HOST-ONLY INVARIANT: a server registered in a DIFFERENT agent (e.g. an
OpenCode datadog server while running in Cursor) is NOT reusable — its tools
are not in this session's tool list — so only the current host's configs are
scanned. When the host cannot be detected, providers resolve to `plugin`
(the plugin-shipped fallback), never to another host's server.

Skills read this snapshot to bind to the right server: when `source` is
`host`, the host's server tools are already in the agent's tool list and the
plugin-shipped server must NOT be registered/used; when `plugin`, the
plugin's .mcp.json server backs the skill; when `none`, the provider's
credentials are unconfigured and the skill should degrade gracefully.

Fail-open: any error here never blocks the session — the map is observability
context, not a gate. Redaction invariant inherited from mcp-registry.py:
env/header values are never read or emitted, only key names.
"""

from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import re
import sys


def _load_mcp_registry():
    here = pathlib.Path(__file__).resolve().parent
    # Marketplace tree: plugins/<plugin>/hooks/scripts/ → repo tools/. Exported
    # bundle: _polymath/support/polymath-core/hooks/scripts/ → a bundled copy.
    candidates = [
        here / "mcp-registry.py",  # exported bundle layout (bundled beside the hook)
        here.parents[3] / "tools" / "mcp-registry.py",  # marketplace tree (plugins/<plugin>/hooks/scripts/)
    ]
    for cand in candidates:
        if cand.exists():
            spec = importlib.util.spec_from_file_location("mcp_registry", cand)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    return None


def _data_root() -> pathlib.Path:
    base = os.environ.get("POLYMATH_PLUGIN_DATA") or os.environ.get("CLAUDE_PLUGIN_DATA")
    if base:
        return pathlib.Path(base)
    data_root = os.environ.get("POLYMATH_DATA_DIR")
    if data_root:
        return pathlib.Path(data_root) / "polymath-core"
    return pathlib.Path.home() / ".polymath" / "data" / "polymath-core"


def _tool_prefix(host: str, server: str) -> str:
    """The tool-name prefix a host's client uses for an MCP server's tools.
    Only naming conventions matter here; per-host quirks live in docs/MCP-REUSE.md."""
    if host == "claude-code":
        return f"mcp__{server}__"
    if host == "gemini-cli":
        return f"mcp_{server}_"
    if host == "opencode":
        return f"{server}_"
    return f"mcp__{server}__"  # cursor, vscode, codex: server-prefixed; exact shape varies


def build_map(registry) -> dict:
    policy = "reuse-host"
    overrides: dict = {}
    ctx_file = _data_root() / "project-context.json"
    ctx: dict = {}
    if ctx_file.exists():
        try:
            ctx = json.loads(ctx_file.read_text())
        except Exception:
            ctx = {}
    mcp_cfg = ctx.get("mcp") or {}
    if isinstance(mcp_cfg, dict):
        policy = mcp_cfg.get("policy") or policy
        so = mcp_cfg.get("serverOverrides")
        if isinstance(so, dict):
            overrides = so

    # HOST-ONLY: scan the CURRENT host's configs. A server registered in
    # another agent is not in this session's tool list — never reusable here.
    detected = registry.detect_host()
    host_entries: list[dict] = []
    if detected is not None:
        entries, _ = registry.scan_host(detected)
        host_entries = entries

    providers: dict = {}
    for ident in registry.collect_provider_identity():
        prov, plugin = ident["provider"], ident["plugin"]
        override = overrides.get(prov)
        if override == "plugin":
            providers[prov] = _entry(ident, "plugin", None, None)
            continue
        order = [1, 0] if policy == "prefer-plugin" else [0, 1]
        resolved = None
        for idx in order:
            if idx == 1:
                resolved = _entry(ident, "plugin", None, None)
                break
            # A name override pins the current host's server to look for (by
            # exact name); otherwise match the provider's declared identity.
            if override:
                candidates = [e for e in host_entries if e["name"] == override]
                if candidates:
                    resolved = _entry(ident, "host", candidates[0], "name-override")
                    break
            else:
                for e in host_entries:
                    signal = registry.match_host_server(e, ident["identity"])
                    if signal:
                        resolved = _entry(ident, "host", e, signal)
                        break
            if resolved:
                break
        providers[prov] = resolved or _entry(ident, "none", None, None)
    return {"policy": policy, "detectedHost": detected, "providers": providers}


def _entry(ident: dict, source: str, host_entry: dict | None, signal: str | None) -> dict:
    prov = ident["provider"]
    out: dict = {
        "capability": ident["capability"],
        "plugin": ident["plugin"],
        "source": source,
    }
    if host_entry is not None:
        name = host_entry["name"]
        out.update({
            "server": name,
            "host": host_entry["host"],
            "scope": host_entry["scope"],
            "matchSignal": signal,
            "toolPrefix": _tool_prefix(host_entry["host"], name),
        })
    else:
        server = ident.get("server") or prov
        out["server"] = server
        out["toolPrefix"] = f"mcp__{server}__"
    return out


def main() -> int:
    try:
        registry = _load_mcp_registry()
        if registry is None:
            return 0  # fail-open: no scanner available, no map
        mcp_map = build_map(registry)
        if not mcp_map.get("providers"):
            return 0
        ctx_file = _data_root() / "project-context.json"
        ctx: dict = {}
        if ctx_file.exists():
            try:
                ctx = json.loads(ctx_file.read_text())
            except Exception:
                ctx = {}
        ctx["mcpResolution"] = mcp_map
        ctx_file.parent.mkdir(parents=True, exist_ok=True)
        ctx_file.write_text(json.dumps(ctx, indent=2))
        # Quiet by default: the map is written for skills to read; the
        # SessionStart hook surfaces a one-line summary only when something
        # changed materially (a reuse resolved to the current host's server).
        reused = [p for p, e in mcp_map["providers"].items() if e.get("source") == "host"]
        if reused:
            host = mcp_map.get("detectedHost") or "current host"
            print(
                f"Polymath: reusing {host} MCP server(s) for: "
                + ", ".join(sorted(reused))
                + " (details in project-context.json mcpResolution)"
            )
    except Exception as e:
        print(f"polymath-core: mcp availability map skipped ({e})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
