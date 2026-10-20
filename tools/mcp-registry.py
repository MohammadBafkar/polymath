#!/usr/bin/env python3
"""Host MCP registry — detect MCP servers already registered in AI coding
agents, match them against Polymath's connector bindings, and render
host-correct MCP config fragments.

Why this exists: a host agent (Claude Code, Cursor, Gemini CLI, OpenCode,
Codex, VS Code) that already has e.g. a datadog MCP registered must never get
a second copy launched under it — duplicate tools, duplicate context, name
collisions. And plugin-shipped `npx` definitions frequently never start at all
(placeholder npm names) or fail auth (credentials not configured).

The default, therefore: REUSE the current host's own MCP servers. Polymath
plugins never ship an auto-registered MCP config — connector servers live as
render TEMPLATES in each plugin's `mcp/servers.json` (Claude-Code-shaped, env
keys only) and become a real server only when the user runs `render` and
installs the fragment into their host config. When no host server matches,
the provider resolves to `none`: the skill degrades gracefully and asks
before installing anything.

This tool closes that gap:

  scan    — parse the CURRENT host's MCP config locations (project + user
            scopes) into one normalized inventory. Env/header VALUES are
            redacted: only key names are reported, never secret values.
            The current host is detected from in-session env markers; the
            host's own registered servers are the only ones reusable in
            this session. --all-hosts widens the view to diagnostics only.
  match   — reconcile the current host's inventory against every connector
            binding's provider identity (bindings/<provider>/binding.json
            `mcp` block) and report reuse-or-install per provider.
  render  — emit host-correct config fragments from a plugin's `mcp/servers.json`
            template (per-host wrapper key, env syntax, and command array shape).
  doctor  — offline health report: placeholder packages, unresolved servers,
            cross-scope duplicates.

Hosts and config locations (researched 2026-10, see docs/MCP-REUSE.md):

  claude-code   project: .mcp.json                user/local: ~/.claude.json (top-level mcpServers + projects[path].mcpServers)
  cursor        project: .cursor/mcp.json         global:     ~/.cursor/mcp.json
  gemini-cli    project: .gemini/settings.json    user:       ~/.gemini/settings.json
  opencode      project: opencode.json(c)         global:     ~/.config/opencode/opencode.json(c)   (v1: mcp.<name>; v2: mcp.servers.<name>)
  codex         project: .codex/config.toml       user:       ~/.codex/config.toml                  (TOML [mcp_servers.<name>])
  vscode        project: .vscode/mcp.json         —           (JSON `servers` key)

Offline and hermetic: no network, no config writes (render writes only to
the directory the caller passes). Fail-open per host — one unparseable
config never hides the others.

Usage:
  tools/mcp-registry.py scan                      # current host's inventory (redacted)
  tools/mcp-registry.py scan --json               # machine-readable
  tools/mcp-registry.py scan --all-hosts          # diagnostics only — servers from OTHER hosts are NOT reusable in this session
  tools/mcp-registry.py match                     # bindings vs current host inventory
  tools/mcp-registry.py render --plugin polymath-observability --target cursor [--out DIR]
  tools/mcp-registry.py render --all [--out DIR]  # every connector, every host
  tools/mcp-registry.py doctor
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
PLUGINS_DIR = REPO / "plugins"

HOSTS = ("claude-code", "cursor", "gemini-cli", "opencode", "codex", "vscode")

# In-session env markers: the env var each agent sets in ITS OWN session (and
# in the child processes it spawns, which includes hook scripts and MCP
# servers). This is how polymath knows which host it is running inside — the
# ONLY host whose registered MCP servers are reusable, because a server
# registered in OpenCode is not in the Cursor session's tool list.
# Verified against agent source/docs 2026-10 (see docs/MCP-REUSE.md).
HOST_ENV_MARKERS = {
    "claude-code": ("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT", "CLAUDE_SESSION_ID"),
    "cursor": ("CURSOR_AGENT", "CURSOR_TRACE_ID", "CURSOR_SESSION_ID"),
    "gemini-cli": ("GEMINI_CLI", "GEMINI_PROJECT_DIR"),
    "opencode": ("OPENCODE", "OPENCODE_PID", "OPENCODE_CLIENT"),
    "codex": ("CODEX_THREAD_ID", "CODEX_SANDBOX"),
    "vscode": ("VSCODE_PID", "VSCODE_CWD", "VSCODE_GIT_ASKPASS_MAIN"),
}


def detect_host() -> str | None:
    """The host agent polymath is currently running inside, or None.

    Matched on in-session env markers, forks first (an OpenCode fork sets both
    its own marker and OPENCODE=1). Returns the FIRST match in HOSTS order.
    """
    for host in HOSTS:
        for var in HOST_ENV_MARKERS.get(host, ()):
            if os.environ.get(var):
                return host
    return None


# ---------------------------------------------------------------------------
# Canonical normalized entry
# ---------------------------------------------------------------------------

def canonical_entry(name: str, spec: dict, host: str, scope: str, path: pathlib.Path) -> dict:
    """Normalize a host-specific server spec to the canonical shape.

    Redaction invariant: env/header VALUES never survive this function —
    only key names. Scanned configs frequently hold literal tokens; this
    tool must be safe to run and share output.
    """
    spec = spec if isinstance(spec, dict) else {}
    command = spec.get("command")
    args = spec.get("args")
    if isinstance(command, list):
        # OpenCode-style command array: command + args are one list.
        args = command[1:] if len(command) > 1 else []
        command = command[0] if command else None
    entry: dict = {
        "name": name,
        "host": host,
        "scope": scope,
        "source": str(path),
    }
    url = spec.get("url") or spec.get("httpUrl")
    if url:
        entry["transport"] = "http"
        entry["url"] = url
        headers = spec.get("headers") or {}
        entry["headerKeys"] = sorted(headers) if isinstance(headers, dict) else []
    else:
        entry["transport"] = "stdio"
        entry["command"] = command
        if args:
            entry["args"] = args
        env = spec.get("env") or spec.get("environment") or {}
        entry["envKeys"] = sorted(env) if isinstance(env, dict) else []
    return entry


def package_of(entry: dict) -> str | None:
    """The npm package (or binary) a stdio entry launches, for matching."""
    args = entry.get("args") or []
    if entry.get("command") in ("npx", "bunx", "uvx", "pnpm dlx", "yarn dlx"):
        for tok in args:
            if not str(tok).startswith("-"):
                return str(tok)
    return entry.get("command")


# ---------------------------------------------------------------------------
# Per-host parsers
# ---------------------------------------------------------------------------

def _json_loadc(path: pathlib.Path) -> dict | None:
    """JSON/JSONC parse: strip // and /* */ comments, trailing commas."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"(^|\s)//[^\n]*", r"\1", text)
    text = re.sub(r",(\s*[}\]])", r"\1", text)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _toml_mcp_servers(path: pathlib.Path) -> dict | None:
    """Minimal TOML subset parse for [mcp_servers.<name>] tables.

    Avoids a tomli dependency: handles the fields Codex configs use
    (string / string-array / inline string-map). A parse failure returns
    None (fail-open) rather than a wrong answer.
    """
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    servers: dict = {}
    current: str | None = None
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^\[mcp_servers\.([A-Za-z0-9_-]+)\]$", line)
        if m:
            current = m.group(1)
            servers[current] = {}
            continue
        if line.startswith("["):
            current = None  # some other table
            continue
        if current is None:
            continue
        kv = re.match(r"^([A-Za-z0-9_]+)\s*=\s*(.+)$", line)
        if not kv:
            continue
        key, val = kv.group(1), kv.group(2).strip()
        if val.startswith("["):
            items = re.findall(r'"([^"]*)"', val)
            servers[current][key] = items
        elif val.startswith('"'):
            servers[current][key] = val[1:-1]
        elif val in ("true", "false"):
            servers[current][key] = val == "true"
        else:
            servers[current][key] = val
    return servers or None


def scan_host(host: str) -> tuple[list[dict], list[str]]:
    """Return (entries, warnings) for one host's project + user scopes."""
    entries: list[dict] = []
    warnings: list[str] = []
    home = pathlib.Path.home()

    def add_json_map(mcp_map: dict | None, host: str, scope: str, path: pathlib.Path) -> None:
        if mcp_map is None:
            return
        for name, spec in mcp_map.items():
            entries.append(canonical_entry(name, spec, host, scope, path))

    if host == "claude-code":
        project = pathlib.Path.cwd() / ".mcp.json"
        if project.exists():
            data = _json_loadc(project)
            if data is None:
                warnings.append(f"unparseable: {project}")
            else:
                add_json_map(data.get("mcpServers"), host, "project", project)
        clauderc = home / ".claude.json"
        if clauderc.exists():
            data = _json_loadc(clauderc)
            if data is None:
                warnings.append(f"unparseable: {clauderc}")
            else:
                add_json_map(data.get("mcpServers"), host, "user", clauderc)
                for proj_path, proj in (data.get("projects") or {}).items():
                    if isinstance(proj, dict) and proj.get("mcpServers"):
                        scope = "local" if proj_path == str(pathlib.Path.cwd()) else "local-other"
                        add_json_map(proj["mcpServers"], host, scope, clauderc)

    elif host == "cursor":
        for scope, path in (("project", pathlib.Path.cwd() / ".cursor" / "mcp.json"),
                            ("user", home / ".cursor" / "mcp.json")):
            if path.exists():
                data = _json_loadc(path)
                if data is None:
                    warnings.append(f"unparseable: {path}")
                else:
                    add_json_map(data.get("mcpServers"), host, scope, path)

    elif host == "gemini-cli":
        for scope, path in (("project", pathlib.Path.cwd() / ".gemini" / "settings.json"),
                            ("user", home / ".gemini" / "settings.json")):
            if path.exists():
                data = _json_loadc(path)
                if data is None:
                    warnings.append(f"unparseable: {path}")
                else:
                    add_json_map(data.get("mcpServers"), host, scope, path)

    elif host == "opencode":
        for path in (pathlib.Path.cwd() / "opencode.json",
                     pathlib.Path.cwd() / "opencode.jsonc",
                     home / ".config" / "opencode" / "opencode.json",
                     home / ".config" / "opencode" / "opencode.jsonc"):
            if path.exists():
                data = _json_loadc(path)
                if data is None:
                    warnings.append(f"unparseable: {path}")
                    continue
                mcp = data.get("mcp") or {}
                # v1 puts names directly under mcp; v2 nests them under mcp.servers.
                for name, spec in mcp.items():
                    if name == "servers" and isinstance(spec, dict):
                        add_json_map(spec, host, "project" if path.parent == pathlib.Path.cwd() else "user", path)
                    elif isinstance(spec, dict):
                        scope = "project" if path.parent == pathlib.Path.cwd() else "user"
                        entries.append(canonical_entry(name, spec, host, scope, path))

    elif host == "codex":
        for scope, path in (("project", pathlib.Path.cwd() / ".codex" / "config.toml"),
                            ("user", home / ".codex" / "config.toml")):
            if path.exists():
                servers = _toml_mcp_servers(path)
                if servers is None:
                    warnings.append(f"no [mcp_servers.*] tables found: {path}")
                else:
                    add_json_map(servers, host, scope, path)

    elif host == "vscode":
        path = pathlib.Path.cwd() / ".vscode" / "mcp.json"
        if path.exists():
            data = _json_loadc(path)
            if data is None:
                warnings.append(f"unparseable: {path}")
            else:
                # VS Code uses `servers` (not `mcpServers`).
                add_json_map(data.get("servers") or data.get("mcpServers"), host, "project", path)

    return entries, warnings


# ---------------------------------------------------------------------------
# Provider identity (from bindings)
# ---------------------------------------------------------------------------

def collect_provider_identity() -> list[dict]:
    """Every kind=mcp binding's identity: provider/capability/plugin + the
    mcp matching block (serverAliases/packages/remoteUrls/envKeys) + the
    plugin's mcp/servers.json render template (if any)."""
    out: list[dict] = []
    for path in sorted(PLUGINS_DIR.glob("*/bindings/*/binding.json")):
        try:
            body = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        transport = body.get("transport") or {}
        if transport.get("kind") != "mcp":
            continue
        plugin_dir = PLUGINS_DIR / path.relative_to(PLUGINS_DIR).parts[0]
        shipped: dict | None = None
        servers_file = plugin_dir / "mcp" / "servers.json"
        if servers_file.exists():
            try:
                shipped = (json.loads(servers_file.read_text()) or {}).get("mcpServers", {}).get(
                    transport.get("server") or ""
                )
            except Exception:
                shipped = None
        out.append({
            "provider": body.get("provider"),
            "capability": body.get("capability"),
            "plugin": plugin_dir.name,
            "identity": body.get("mcp") or {},
            "server": transport.get("server"),
            "shipped": shipped,
        })
    return out


def match_host_server(entry: dict, identity: dict) -> str | None:
    """Does a host-registered entry belong to this provider's identity?

    Match signals, strongest first: server name alias, remote URL endpoint,
    npm package token in the launch args. Returns the signal or None.
    """
    aliases = set(identity.get("serverAliases") or [])
    if entry.get("name") in aliases:
        return "name"
    urls = set(identity.get("remoteUrls") or [])
    if entry.get("url") and _endpoint(entry["url"]) in {_endpoint(u) for u in urls}:
        return "url"
    pkgs = set(identity.get("packages") or [])
    if pkgs and package_of(entry) in pkgs:
        return "package"
    return None


def _endpoint(url: str) -> str:
    """Canonical endpoint for URL matching: scheme/host/path, query stripped
    (query strings carry per-client tracking params like referrer_ide), case
    and default port/trailing slash normalized. A different path = a
    different server."""
    url = url.strip().rstrip("/")
    url = url.split("?", 1)[0]
    url = re.sub(r":(443|80)$", "", url)
    return url.lower()


# ---------------------------------------------------------------------------
# Render: plugin mcp/servers.json template → per-host config fragments
# ---------------------------------------------------------------------------

# Per-host env expansion syntax. Credentials are ALWAYS rendered as env-var
# references — a render never copies a literal secret between hosts.
def _env_expr(var: str, host: str) -> str:
    if host == "claude-code":
        return "${%s:-}" % var
    if host == "cursor":
        return "${env:%s}" % var
    if host == "gemini-cli":
        return "${%s}" % var
    if host == "opencode":
        return "{env:%s}" % var
    return "${%s}" % var  # vscode; codex handled separately (no expansion)


def _derive_env_var(server: str, key: str) -> str:
    """Env var name a render references for a server env key: the key itself
    when it is already UPPER_SNAKE (the server-native name), else derived."""
    return key if re.match(r"^[A-Z][A-Z0-9_]*$", key) else key.upper()


def render_fragment(servers: dict, host: str) -> dict | str | None:
    """Render {server: spec} (canonical Claude-Code-shaped specs) into the
    host's config shape. Returns None when a host is unsupported."""
    if host in ("claude-code", "cursor", "gemini-cli"):
        out = {}
        for name, spec in servers.items():
            entry: dict = {"type": spec.get("type", "stdio")}
            if spec.get("url"):
                if host == "gemini-cli":
                    entry = {"httpUrl": spec["url"]}
                    headers = spec.get("headers") or {}
                    if headers:
                        entry["headers"] = {
                            k: _env_expr(_derive_env_var(name, k), host)
                            for k in headers
                        }
                else:
                    entry["url"] = spec["url"]
                    headers = spec.get("headers") or {}
                    if headers:
                        entry["headers"] = {
                            k: _env_expr(_derive_env_var(name, k), host)
                            for k in headers
                        }
            else:
                entry["command"] = spec.get("command")
                if spec.get("args"):
                    entry["args"] = spec["args"]
                env = spec.get("env") or {}
                if env:
                    entry["env"] = {
                        k: _env_expr(_derive_env_var(name, k), host) for k in env
                    }
            out[name] = entry
        if host == "claude-code":
            return {"mcpServers": out}
        return {"mcpServers": out}  # cursor + gemini use mcpServers too

    if host == "opencode":
        out = {}
        for name, spec in servers.items():
            if spec.get("url"):
                entry: dict = {
                    "type": "remote",
                    "url": spec["url"],
                    "enabled": True,
                }
                headers = spec.get("headers") or {}
                if headers:
                    entry["headers"] = {
                        k: _env_expr(_derive_env_var(name, k), host) for k in headers
                    }
            else:
                entry = {
                    "type": "local",
                    "command": [spec.get("command")] + list(spec.get("args") or []),
                    "enabled": True,
                }
                env = spec.get("env") or {}
                if env:
                    entry["environment"] = {
                        k: _env_expr(_derive_env_var(name, k), host) for k in env
                    }
            out[name] = entry
        return {"mcp": out}

    if host == "vscode":
        out = {}
        for name, spec in servers.items():
            entry = {"type": spec.get("type", "stdio")}
            if spec.get("url"):
                entry["url"] = spec["url"]
            else:
                entry["command"] = spec.get("command")
                if spec.get("args"):
                    entry["args"] = spec["args"]
                env = spec.get("env") or {}
                if env:
                    entry["env"] = {
                        k: _env_expr(_derive_env_var(name, k), host) for k in env
                    }
            out[name] = entry
        return {"servers": out}

    if host == "codex":
        # TOML: env has no expansion — env_vars forwards the names from the
        # local environment instead.
        lines: list[str] = []
        for name, spec in servers.items():
            lines.append(f"[mcp_servers.{name}]")
            if spec.get("url"):
                lines.append(f'url = "{spec["url"]}"')
            else:
                lines.append(f'command = "{spec.get("command")}"')
                if spec.get("args"):
                    lines.append("args = " + json.dumps(spec["args"]))
                env = spec.get("env") or {}
                if env:
                    lines.append("env_vars = " + json.dumps(sorted(env)))
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"

    return None


def plugin_servers(plugin: str) -> dict:
    """The plugin's renderable server template (mcp/servers.json, Claude-Code
    shape). Empty when the plugin ships no template — templates are render
    inputs, never auto-registered configs."""
    path = PLUGINS_DIR / plugin / "mcp" / "servers.json"
    if not path.exists():
        return {}
    return (json.loads(path.read_text()) or {}).get("mcpServers", {})


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def _scan_hosts(all_hosts: bool) -> tuple[list[dict], list[str], str | None]:
    """Scan the current host (default) or every host (--all-hosts).

    Returns (entries, warnings, detected_host). Detection is env-marker
    based; when it cannot identify the host, the caller surfaces that and
    scans nothing rather than guessing (a wrong guess would map providers
    onto servers the session cannot call).
    """
    if all_hosts:
        hosts = list(HOSTS)
        detected = detect_host()
    else:
        detected = detect_host()
        if detected is None:
            return [], ["could not detect the running host agent (no in-session env marker set); not scanning any host config"], None
        hosts = [detected]
    all_entries: list[dict] = []
    warnings: list[str] = []
    for host in hosts:
        entries, warns = scan_host(host)
        all_entries.extend(entries)
        warnings.extend(f"{host}: {w}" for w in warns)
    return all_entries, warnings, detected


def cmd_scan(args: argparse.Namespace) -> int:
    all_entries, warnings, detected = _scan_hosts(args.all_hosts)

    if args.json:
        print(json.dumps({
            "detectedHost": detected,
            "servers": all_entries,
            "warnings": warnings,
            "note": None if (args.all_hosts or detected) else "pass --all-hosts to inspect other agents' configs (diagnostics only)",
        }, indent=2))
        return 0

    if not args.all_hosts:
        print(f"Detected host: {detected or 'unknown (no in-session env marker — run inside your agent, or pass --all-hosts for diagnostics)'}")
    if not all_entries:
        print("No host-registered MCP servers found.")
    else:
        label = "host-registered" if not args.all_hosts else "host-registered (ALL hosts — cross-host servers are NOT reusable in this session)"
        print(f"{len(all_entries)} {label} MCP server(s):\n")
        print(f"{'host':12} {'scope':12} {'name':24} transport  identity")
        for e in all_entries:
            ident = e.get("url") or package_of(e) or "?"
            print(
                f"{e['host']:12} {e['scope']:12} {e['name']:24} "
                f"{e['transport']:9}  {ident}"
            )
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  - {w}")
    return 0


def cmd_match(args: argparse.Namespace) -> int:
    identities = collect_provider_identity()
    host_entries, warnings, detected = _scan_hosts(args.all_hosts)

    rows: list[dict] = []
    for ident in identities:
        found: tuple[str, dict] | None = None
        for e in host_entries:
            signal = match_host_server(e, ident["identity"])
            if signal:
                found = (signal, e)
                break
        rows.append({
            "provider": ident["provider"],
            "capability": ident["capability"],
            "plugin": ident["plugin"],
            "reuse": found is not None,
            "signal": found[0] if found else None,
            "hostServer": (
                {"name": found[1]["name"], "host": found[1]["host"], "scope": found[1]["scope"]}
                if found else None
            ),
        })

    if args.json:
        print(json.dumps({
            "detectedHost": detected,
            "providers": rows,
            "warnings": warnings,
        }, indent=2))
        return 0

    print(f"Detected host: {detected or 'unknown'}\n")
    print(f"{'provider':26} {'capability':24} reuse  host server")
    for r in rows:
        if r["reuse"]:
            hs = r["hostServer"]
            where = f"{hs['host']}/{hs['scope']}"
            print(
                f"{r['provider']:26} {r['capability']:24} yes    "
                f"{hs['name']} ({where}, matched by {r['signal']})"
            )
        else:
            print(
                f"{r['provider']:26} {r['capability']:24} no     "
                f"(nothing registered in this host — do not install without asking)"
            )
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  - {w}")
    n_reuse = sum(1 for r in rows if r["reuse"])
    scope = detected or "current host"
    print(f"\n{n_reuse}/{len(rows)} mcp-bound provider(s) resolved from {scope} servers.")
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    out_root = pathlib.Path(args.out) if args.out else pathlib.Path.cwd() / ".polymath" / "mcp"
    plugins = sorted({p.relative_to(PLUGINS_DIR).parts[0]
                      for p in PLUGINS_DIR.glob("*/mcp/servers.json")}) if args.all else [args.plugin]
    targets = list(HOSTS) if not args.target else [args.target]
    written = 0
    for plugin in plugins:
        servers = plugin_servers(plugin)
        if not servers:
            if not args.all:
                print(f"{plugin}: no mcp/servers.json template", file=sys.stderr)
                return 1
            continue
        for target in targets:
            frag = render_fragment(servers, target)
            if frag is None:
                print(f"{plugin}: unsupported target {target}", file=sys.stderr)
                return 1
            dest = out_root / target
            dest.mkdir(parents=True, exist_ok=True)
            if target == "codex":
                path = dest / f"{plugin}.mcp.toml"
                path.write_text(frag, encoding="utf-8")
            else:
                path = dest / f"{plugin}.mcp.json"
                path.write_text(json.dumps(frag, indent=2) + "\n", encoding="utf-8")
            print(f"wrote {path.relative_to(out_root.parent)}")
            written += 1
    print(f"\n{written} fragment(s) under {out_root}/")
    print("Fragments reference env vars only — set the variables in your shell profile; no secret is written.")
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    import importlib.util as _ilu
    _spec = _ilu.spec_from_file_location(
        "check_mcp_packages", REPO / "tools" / "check-mcp-packages.py"
    )
    _cmp = _ilu.module_from_spec(_spec)
    _spec.loader.exec_module(_cmp)
    VERIFIED, UNVERIFIED, package_from_args = (
        _cmp.VERIFIED, _cmp.UNVERIFIED, _cmp.package_from_args,
    )

    problems: list[str] = []
    identities = collect_provider_identity()
    host_entries, warnings, detected = _scan_hosts(False)
    if detected is None:
        print("mcp-registry doctor: could not detect the running host agent — "
              "run inside your agent session (or use `scan --all-hosts` for diagnostics).")
        return 0

    # 1. Cross-scope duplicate server names within a host.
    seen: dict[tuple, list[dict]] = {}
    for e in host_entries:
        seen.setdefault((e["host"], e["name"]), []).append(e)
    for (host, name), group in sorted(seen.items()):
        if len(group) > 1:
            scopes = ", ".join(sorted({g["scope"] for g in group}))
            problems.append(f"{host}: server '{name}' registered at multiple scopes ({scopes})")

    # 2. Placeholder/unresolved packages in the plugin render templates, and
    #    whether a host-registered server already covers the provider (reuse
    #    makes the dead package irrelevant — templates are never launched
    #    directly).
    for ident in identities:
        shipped = ident.get("shipped") or {}
        pkg = None
        if shipped.get("command") == "npx":
            pkg = package_from_args(shipped.get("args") or [])
        reused = any(match_host_server(e, ident["identity"]) for e in host_entries)
        if pkg and pkg in UNVERIFIED:
            if reused:
                continue  # host server covers it; the dead package never launches a session tool
            problems.append(
                f"{ident['provider']}: template package '{pkg}' does not resolve on npm and no host-registered "
                f"match — register the vendor's real server (render a fragment via the render subcommand)"
            )
        if pkg and pkg not in VERIFIED and pkg not in UNVERIFIED:
            problems.append(f"{ident['provider']}: unclassified package '{pkg}' (MCP-PKG)")

    # 3. Env vars a reused host server still needs, referenced but unset.
    for ident in identities:
        for e in host_entries:
            signal = match_host_server(e, ident["identity"])
            if not signal:
                continue
            missing = [k for k in e.get("envKeys", []) if not pathlib.os.environ.get(k)]
            if missing:
                print(
                    f"note: {e['host']}/{e['scope']} server '{e['name']}' "
                    f"({ident['provider']}) references unset env var(s): {', '.join(missing)}"
                )
            break

    if args.json:
        print(json.dumps({"problems": problems}, indent=2))
    if problems:
        print(f"mcp-registry doctor: {len(problems)} problem(s):")
        for p in problems:
            print(f"  ✗ {p}")
        return 1
    print("mcp-registry doctor: no problems found.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("scan", help="inventory the current host's registered MCP servers (redacted)")
    p.add_argument("--json", action="store_true")
    p.add_argument("--all-hosts", action="store_true",
                   help="scan every agent's configs (diagnostics only — cross-host servers are NOT reusable in this session)")
    p.set_defaults(fn=cmd_scan)

    p = sub.add_parser("match", help="reconcile connector bindings vs the current host inventory")
    p.add_argument("--json", action="store_true")
    p.add_argument("--all-hosts", action="store_true",
                   help="scan every agent's configs (diagnostics only — cross-host servers are NOT reusable in this session)")
    p.set_defaults(fn=cmd_match)

    p = sub.add_parser("render", help="render host-correct MCP config fragments")
    p.add_argument("--plugin", help="plugin name (e.g. polymath-observability)")
    p.add_argument("--all", action="store_true", help="every connector plugin")
    p.add_argument("--target", choices=HOSTS, help="one host (default: all)")
    p.add_argument("--out", help="output dir (default: .polymath/mcp/)")
    p.set_defaults(fn=cmd_render)

    p = sub.add_parser("doctor", help="offline health report")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_doctor)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
