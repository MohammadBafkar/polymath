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
        "source": "host",                  # host | none
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
scanned.

NO AUTO-REGISTERED FALLBACK: Polymath plugins never auto-register MCP
servers — there is no plugin `.mcp.json` to launch duplicates or fail auth.
When the current host has no matching server, the provider resolves to
`none` (with a `note` naming the pinned server when a `serverOverrides` pin
did not match): the skill degrades gracefully and asks before helping the
user install anything. The plugin's `mcp/servers.json` template renders a
host-correct fragment via `mcp-registry render`, applied only on request;
the `plugin` pin and the `prefer-plugin` policy select the template's server
NAME, which is only usable once the user registers it in this host.

Skills read this snapshot to bind to the right server: when `source` is
`host`, the host's server tools are already in the agent's tool list; when
`none`, the skill must degrade gracefully rather than call tools absent
from the session.

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
    # Must resolve exactly like load-project-context.py's _data_root, or the
    # mcpResolution block lands in a different file than the snapshot it
    # annotates (CLAUDE_PLUGIN_DATA is a plugin data dir; the snapshot lives
    # in its polymath-core/ subdirectory).
    plugin_base = os.environ.get("POLYMATH_PLUGIN_DATA")
    if plugin_base:
        return pathlib.Path(plugin_base)
    data_root = os.environ.get("POLYMATH_DATA_DIR")
    if data_root:
        return pathlib.Path(data_root) / "polymath-core"
    legacy_base = os.environ.get("CLAUDE_PLUGIN_DATA")
    if legacy_base:
        return pathlib.Path(legacy_base) / "polymath-core"
    return pathlib.Path.home() / ".polymath" / "data" / "polymath-core"


def _mirror_file(ctx_file: pathlib.Path) -> pathlib.Path | None:
    """The portable snapshot copy load-project-context.py keeps for Bash-tool readers."""
    if os.environ.get("POLYMATH_PLUGIN_DATA") or os.environ.get("POLYMATH_DATA_DIR"):
        return None
    if not os.environ.get("CLAUDE_PLUGIN_DATA"):
        return None
    mirror = pathlib.Path.home() / ".polymath" / "data" / "polymath-core" / ctx_file.name
    return None if mirror == ctx_file else mirror


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
        template_name = ident.get("server") or prov
        if override == "plugin":
            # Explicit pin to the plugin's mcp/servers.json template: the
            # intended server is the one registered under the template's
            # server name (never an auto-registered copy).
            override = template_name
        if override:
            # A name override pins the current host's server to look for (by
            # exact name).
            candidates = [e for e in host_entries if e["name"] == override]
            if candidates:
                providers[prov] = _entry(ident, "host", candidates[0], "name-override")
            elif override == template_name:
                providers[prov] = _entry(
                    ident, "none", None, None,
                    note=(f"pinned to the plugin template server '{override}' — not registered in this host yet; "
                          f"opt in via `mcp-registry render --plugin {plugin}`"),
                )
            else:
                providers[prov] = _entry(
                    ident, "none", None, None,
                    note=f"pinned server '{override}' not found in {detected or 'the current host'}'s config",
                )
            continue
        resolved = None
        if policy == "prefer-plugin":
            # The plugin template's server is the intended one; still only
            # usable once the user has registered it in this host.
            for e in host_entries:
                if e["name"] == template_name:
                    resolved = _entry(ident, "host", e, "name-override")
                    break
        if resolved is None:
            for e in host_entries:
                signal = registry.match_host_server(e, ident["identity"])
                if signal:
                    resolved = _entry(ident, "host", e, signal)
                    break
        providers[prov] = resolved or _entry(ident, "none", None, None)
    return {"policy": policy, "detectedHost": detected, "providers": providers}


def _entry(ident: dict, source: str, host_entry: dict | None, signal: str | None,
           note: str | None = None) -> dict:
    prov = ident["provider"]
    out: dict = {
        "capability": ident["capability"],
        "plugin": ident["plugin"],
        "source": source,
    }
    if note:
        out["note"] = note
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
        # Server name to register UNDER once the user opts in (render +
        # install). No host tools exist yet — the skill must degrade
        # gracefully rather than call tools that are absent from the session.
        server = ident.get("server") or prov
        out["server"] = server
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
        mirror = _mirror_file(ctx_file)
        if mirror is not None:
            mirror.parent.mkdir(parents=True, exist_ok=True)
            mirror.write_text(json.dumps(ctx, indent=2))
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
