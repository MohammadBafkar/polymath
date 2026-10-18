"""Tests for tools/mcp-registry.py — host detection and current-host-only
resolution (the host-only invariant: a server registered in a DIFFERENT agent
is never reusable; only the current host's configs are scanned).

Run with: python3 -m unittest discover -s tests/tools
"""

from __future__ import annotations

import importlib.util
import os
import pathlib
import sys
import unittest
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

_spec = importlib.util.spec_from_file_location("mcp_registry", REPO_ROOT / "tools" / "mcp-registry.py")
mcp_registry = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mcp_registry)


def _clean_env() -> dict:
    """Wipe every host marker so detection starts from a clean slate."""
    env = dict(os.environ)
    for markers in mcp_registry.HOST_ENV_MARKERS.values():
        for var in markers:
            env.pop(var, None)
    return env


class DetectHostTests(unittest.TestCase):
    def test_claude_code_marker(self) -> None:
        with mock.patch.dict(os.environ, {**_clean_env(), "CLAUDECODE": "1"}):
            self.assertEqual(mcp_registry.detect_host(), "claude-code")

    def test_cursor_marker(self) -> None:
        with mock.patch.dict(os.environ, {**_clean_env(), "CURSOR_AGENT": "1"}):
            self.assertEqual(mcp_registry.detect_host(), "cursor")

    def test_opencode_marker(self) -> None:
        with mock.patch.dict(os.environ, {**_clean_env(), "OPENCODE": "1"}):
            self.assertEqual(mcp_registry.detect_host(), "opencode")

    def test_gemini_marker(self) -> None:
        with mock.patch.dict(os.environ, {**_clean_env(), "GEMINI_CLI": "1"}):
            self.assertEqual(mcp_registry.detect_host(), "gemini-cli")

    def test_no_marker_returns_none(self) -> None:
        with mock.patch.dict(os.environ, _clean_env(), clear=True):
            self.assertIsNone(mcp_registry.detect_host())


class HostOnlyMatchTests(unittest.TestCase):
    """The host-only invariant: match against ONLY the given entries."""

    def test_name_match(self) -> None:
        identity = {"serverAliases": ["datadog"]}
        entry = {"name": "datadog", "transport": "http", "url": "https://mcp.datadoghq.com/mcp"}
        self.assertEqual(mcp_registry.match_host_server(entry, identity), "name")

    def test_url_match_ignores_query_and_case(self) -> None:
        identity = {"remoteUrls": ["https://mcp.datadoghq.com/api/unstable/mcp-server/mcp"]}
        entry = {
            "name": "my-dd",
            "transport": "http",
            "url": "https://MCP.datadoghq.com/api/unstable/mcp-server/mcp?plugin_version=0.7",
        }
        self.assertEqual(mcp_registry.match_host_server(entry, identity), "url")

    def test_package_match(self) -> None:
        identity = {"packages": ["@datadog/mcp-server"]}
        entry = {"name": "weird-name", "transport": "stdio", "command": "npx", "args": ["-y", "@datadog/mcp-server"]}
        self.assertEqual(mcp_registry.match_host_server(entry, identity), "package")

    def test_no_identity_signal_no_match(self) -> None:
        entry = {"name": "datadog", "transport": "http", "url": "https://mcp.datadoghq.com/mcp"}
        self.assertIsNone(mcp_registry.match_host_server(entry, {}))

    def test_different_name_package_and_url_never_matches(self) -> None:
        identity = {"serverAliases": ["datadog"], "packages": ["@datadog/mcp-server"]}
        entry = {"name": "other", "transport": "stdio", "command": "npx", "args": ["-y", "@other/pkg"]}
        self.assertIsNone(mcp_registry.match_host_server(entry, identity))


class CanonicalEntryRedactionTests(unittest.TestCase):
    def test_env_values_never_survive(self) -> None:
        spec = {
            "type": "stdio",
            "command": "npx",
            "args": ["-y", "@datadog/mcp-server"],
            "env": {"DD_API_KEY": "super-secret-value", "DD_SITE": "datadoghq.eu"},
        }
        entry = mcp_registry.canonical_entry("dd", spec, "opencode", "user", pathlib.Path("/x"))
        self.assertEqual(entry["envKeys"], ["DD_API_KEY", "DD_SITE"])
        blob = repr(entry)
        self.assertNotIn("super-secret-value", blob)
        self.assertNotIn("datadoghq.eu", blob)  # value redacted; key names only

    def test_header_values_never_survive(self) -> None:
        spec = {
            "url": "https://mcp.example.com",
            "headers": {"Authorization": "Bearer tok-123"},
        }
        entry = mcp_registry.canonical_entry("x", spec, "cursor", "user", pathlib.Path("/x"))
        self.assertEqual(entry["headerKeys"], ["Authorization"])
        self.assertNotIn("tok-123", repr(entry))

    def test_opencode_command_array_normalizes(self) -> None:
        spec = {"type": "local", "command": ["npx", "-y", "@sentry/mcp-server"], "environment": {"SENTRY_AUTH_TOKEN": "v"}}
        entry = mcp_registry.canonical_entry("sentry", spec, "opencode", "user", pathlib.Path("/x"))
        self.assertEqual(entry["command"], "npx")
        self.assertEqual(entry["args"], ["-y", "@sentry/mcp-server"])
        self.assertEqual(entry["envKeys"], ["SENTRY_AUTH_TOKEN"])


class RenderFragmentTests(unittest.TestCase):
    SERVERS = {
        "datadog": {
            "type": "stdio",
            "command": "npx",
            "args": ["-y", "@datadog/mcp-server"],
            "env": {"DD_API_KEY": "${DD_API_KEY}"},
        }
    }

    def test_cursor_env_syntax(self) -> None:
        frag = mcp_registry.render_fragment(self.SERVERS, "cursor")
        self.assertEqual(frag["mcpServers"]["datadog"]["env"]["DD_API_KEY"], "${env:DD_API_KEY}")

    def test_gemini_env_syntax(self) -> None:
        frag = mcp_registry.render_fragment(self.SERVERS, "gemini-cli")
        self.assertEqual(frag["mcpServers"]["datadog"]["env"]["DD_API_KEY"], "${DD_API_KEY}")

    def test_opencode_shape(self) -> None:
        frag = mcp_registry.render_fragment(self.SERVERS, "opencode")
        entry = frag["mcp"]["datadog"]
        self.assertEqual(entry["type"], "local")
        self.assertEqual(entry["command"], ["npx", "-y", "@datadog/mcp-server"])
        self.assertEqual(entry["environment"]["DD_API_KEY"], "{env:DD_API_KEY}")

    def test_codex_toml_env_vars(self) -> None:
        frag = mcp_registry.render_fragment(self.SERVERS, "codex")
        self.assertIn("[mcp_servers.datadog]", frag)
        self.assertIn('env_vars = ["DD_API_KEY"]', frag)

    def test_vscode_servers_key(self) -> None:
        frag = mcp_registry.render_fragment(self.SERVERS, "vscode")
        self.assertIn("servers", frag)
        self.assertNotIn("mcpServers", frag)

    def test_claude_code_mcpServers_key(self) -> None:
        frag = mcp_registry.render_fragment(self.SERVERS, "claude-code")
        self.assertIn("mcpServers", frag)


if __name__ == "__main__":
    unittest.main()
