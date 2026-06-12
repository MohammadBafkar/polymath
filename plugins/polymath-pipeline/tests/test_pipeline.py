"""Unit tests for bin/polymath-pipeline (loaded via SourceFileLoader — the
script has no .py extension).

Covers:
  - shared root resolver ($HOME / CLAUDE_CONFIG_DIR excluded, .git boundary)
  - routing.mode line-scan (base, overlay-wins, absent → hint)
  - session markers: touch, classification TTL, root-change invalidation,
    mark-newest / mark-creates
  - read-only Bash exemption (modify-pattern blacklist)
  - hook flows: classify directive then silence after mark; enforce deny
    (exit 2) / allow; audited kill switch; fail-open on malformed payloads
  - retention sweep (old markers pruned, oversized log truncated)

Run with: python3 -m unittest discover -s plugins/polymath-pipeline/tests
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import io
import json
import os
import pathlib
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "plugins" / "polymath-pipeline" / "bin" / "polymath-pipeline"


def _import_engine():
    loader = importlib.machinery.SourceFileLoader("polymath_pipeline", str(SCRIPT))
    spec = importlib.util.spec_from_loader("polymath_pipeline", loader)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class PipelineTestCase(unittest.TestCase):
    """Isolated HOME / CLAUDE_PLUGIN_DATA / CLAUDE_CONFIG_DIR / cwd."""

    def setUp(self) -> None:
        self.mod = _import_engine()
        self._tmp = tempfile.TemporaryDirectory()
        self.base = pathlib.Path(self._tmp.name)
        self.repo = self.base / "repo"
        (self.repo / ".polymath").mkdir(parents=True)
        (self.repo / ".git").mkdir()
        self._env = {
            k: os.environ.get(k)
            for k in ("CLAUDE_PLUGIN_DATA", "CLAUDE_CONFIG_DIR", "HOME", "POLYMATH_PIPELINE_OFF")
        }
        os.environ["CLAUDE_PLUGIN_DATA"] = str(self.base / ".pdata")
        os.environ["CLAUDE_CONFIG_DIR"] = str(self.base / ".cfg")
        os.environ["HOME"] = str(self.base / "home")
        os.environ.pop("POLYMATH_PIPELINE_OFF", None)
        (self.base / "home").mkdir()
        self._prev_cwd = pathlib.Path.cwd()
        os.chdir(self.repo)

    def tearDown(self) -> None:
        os.chdir(self._prev_cwd)
        for k, v in self._env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        self._tmp.cleanup()

    def _write_project(self, mode: str | None, overlay_mode: str | None = None) -> None:
        body = "schemaVersion: 1\nproject:\n  name: demo\n"
        if mode:
            body += f"routing:\n  mode: {mode}\n"
        (self.repo / ".polymath" / "project.yaml").write_text(body)
        if overlay_mode:
            (self.repo / ".polymath" / "project.local.yaml").write_text(
                f"routing:\n  mode: {overlay_mode}\n"
            )

    def _hook(self, name: str, payload: dict) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        stdin = io.StringIO(json.dumps(payload))
        prev_stdin = self.mod.sys.stdin
        self.mod.sys.stdin = stdin
        try:
            with redirect_stdout(out), redirect_stderr(err):
                code = self.mod.main([name])
        finally:
            self.mod.sys.stdin = prev_stdin
        return code, out.getvalue(), err.getvalue()

    def _events(self) -> list[str]:
        path = self.base / ".pdata" / "decisions.jsonl"
        if not path.exists():
            return []
        return [json.loads(l)["event"] for l in path.read_text().splitlines()]

    def _mark(self, *argv: str) -> int:
        with redirect_stdout(io.StringIO()):
            return self.mod.main(["mark", *argv])


class RootResolverTests(PipelineTestCase):
    def test_project_root_found_from_nested_dir(self) -> None:
        self._write_project("classify")
        nested = self.repo / "src" / "deep"
        nested.mkdir(parents=True)
        self.assertEqual(self.mod.resolve_root(nested), self.repo.resolve())

    def test_home_is_never_a_root(self) -> None:
        home = pathlib.Path(os.environ["HOME"])
        (home / ".polymath").mkdir(parents=True)
        (home / ".polymath" / "project.yaml").write_text("routing:\n  mode: enforce\n")
        self.assertIsNone(self.mod.resolve_root(home))

    def test_config_dir_is_never_a_root(self) -> None:
        cfg = pathlib.Path(os.environ["CLAUDE_CONFIG_DIR"])
        (cfg / ".polymath").mkdir(parents=True)
        (cfg / ".polymath" / "project.yaml").write_text("routing:\n  mode: enforce\n")
        self.assertIsNone(self.mod.resolve_root(cfg))

    def test_git_boundary_without_project_file(self) -> None:
        bare = self.base / "bare"
        (bare / ".git").mkdir(parents=True)
        sub = bare / "sub"
        sub.mkdir()
        self.assertIsNone(self.mod.resolve_root(sub))


class ModeReaderTests(PipelineTestCase):
    def test_base_mode(self) -> None:
        self._write_project("classify")
        self.assertEqual(self.mod.read_mode(self.repo), "classify")

    def test_overlay_wins(self) -> None:
        self._write_project("classify", overlay_mode="enforce")
        self.assertEqual(self.mod.read_mode(self.repo), "enforce")

    def test_absent_routing_is_hint(self) -> None:
        self._write_project(None)
        self.assertEqual(self.mod.read_mode(self.repo), "hint")

    def test_mode_outside_routing_block_ignored(self) -> None:
        (self.repo / ".polymath" / "project.yaml").write_text(
            "schemaVersion: 1\nrouting:\n  mode: classify\ntracker:\n  mode: enforce\n"
        )
        self.assertEqual(self.mod.read_mode(self.repo), "classify")


class BashBlacklistTests(PipelineTestCase):
    READ_ONLY = [
        "grep -rn TODO src 2>/dev/null | head",
        "ls -la docs/",
        "git status --short",
        "git log --oneline -5",
        "git diff HEAD~1",
        "cat README.md",
        "python3 -c 'print(1)'",
        "curl https://example.com/api",
        "find . -name '*.py' | wc -l",
        # words that the wrapper patterns must NOT catch out of command position
        "echo make it work",
        "gh pr list",
        "gh pr view 123 --comments",
        "az group list",
        "gcloud projects list",
        "aws s3 ls s3://bucket",
        "tar -tzf backup.tgz",
        "tar --list -f archive.tar",
    ]
    MUTATING = [
        "echo done > status.txt",
        "rm -rf build",
        "sed -i '' 's/a/b/' f.txt",
        "git commit -m x",
        "git push origin main",
        "npm install left-pad",
        "tee out.log",
        "docker run -it img",
        "mkdir -p new/dir",
        "curl -o out.bin https://example.com",
        # the 11 sampled mutators the original blacklist missed
        "make",
        "cd ui && make",
        "python3 deploy.py --prod",
        "node scripts/build.js",
        "npx prisma migrate dev",
        "gh pr merge 123 --squash",
        "az group delete -n prod",
        "gcloud compute instances delete vm-1",
        "psql -c 'drop table users'",
        "rsync -av build/ srv:/var/www",
        "patch -p1 < fix.diff",
        "tar -xzf release.tgz",
        # same families, adjacent shapes
        "make install",
        "bash scripts/release.sh",
        "gh workflow run deploy.yml",
        "aws s3 sync build/ s3://bucket",
        "mysql -e 'delete from t'",
        "scp build.tgz srv:/tmp",
        "cat fix.diff | patch -p1",
        "tar czf out.tgz src",
    ]

    def test_read_only_commands_exempt(self) -> None:
        for cmd in self.READ_ONLY:
            self.assertFalse(self.mod.bash_is_mutating(cmd), f"false positive: {cmd}")

    def test_mutating_commands_flagged(self) -> None:
        for cmd in self.MUTATING:
            self.assertTrue(self.mod.bash_is_mutating(cmd), f"missed: {cmd}")

    def test_mark_invocation_is_never_gated(self) -> None:
        # Deadlock guard: the recovery command the deny message prescribes
        # must itself pass the gate, or enforce mode can never be satisfied.
        cmd = (
            '"/home/u/.claude/plugins/cache/polymath/polymath-pipeline/0.3.0'
            '/bin/polymath-pipeline" mark --surface direct --cwd /work/repo'
        )
        self.assertFalse(self.mod.bash_is_mutating(cmd))


class McpClassificationTests(PipelineTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.policy = self.mod.load_tool_policy(None)

    def _gated(self, tool: str) -> bool:
        return self.mod.mcp_is_gated(tool, self.policy)

    def test_mutating_names_gated(self) -> None:
        for tool in [
            "mcp__plugin_polymath-vcs_github__push_files",
            "mcp__plugin_polymath-vcs_github__create_pull_request",
            "mcp__azure-devops__wit_update_work_item",
            "mcp__azure-devops__pipelines_run_pipeline",
            "mcp__claude_ai_Atlassian_Rovo__createConfluencePage",
        ]:
            self.assertTrue(self._gated(tool), f"not gated: {tool}")

    def test_read_only_names_exempt(self) -> None:
        for tool in [
            "mcp__plugin_polymath-vcs_github__get_file_contents",
            "mcp__plugin_polymath-vcs_github__search_code",
            "mcp__azure-devops__repo_list_branches_by_repo",
            "mcp__azure-devops__pipelines_get_run",  # first verb wins: get, not run
            "mcp__claude_ai_Atlassian_Rovo__getConfluencePage",
        ]:
            self.assertFalse(self._gated(tool), f"over-gated: {tool}")

    def test_unknown_verb_defaults_to_gated(self) -> None:
        self.assertTrue(self._gated("mcp__foo__frobnicate_widget"))

    def test_first_verb_wins_over_later_read_verb(self) -> None:
        # a mutating verb leading the name gates it even when a read verb
        # appears later (update_search_index must never pass as a "search")
        self.assertTrue(self._gated("mcp__foo__update_search_index"))


class EnforceGateExtendedTests(PipelineTestCase):
    def _gate(self, tool: str, session: str = "s") -> tuple[int, str]:
        payload = {"session_id": session, "cwd": str(self.repo), "tool_name": tool, "tool_input": {}}
        code, _, err = self._hook("hook-pretool", payload)
        return code, err

    def test_task_denied_until_marked(self) -> None:
        self._write_project("enforce")
        code, err = self._gate("Task")
        self.assertEqual(code, 2)
        self.assertIn("blocked Task", err)
        self._mark("--surface", "direct", "--cwd", str(self.repo))
        code, _ = self._gate("Task")
        self.assertEqual(code, 0)

    def test_mutating_mcp_denied_read_only_mcp_exempt(self) -> None:
        self._write_project("enforce")
        code, err = self._gate("mcp__plugin_polymath-vcs_github__push_files")
        self.assertEqual(code, 2)
        self.assertIn("push_files", err)
        code, _ = self._gate("mcp__plugin_polymath-vcs_github__get_file_contents")
        self.assertEqual(code, 0)
        self._mark("--surface", "direct", "--cwd", str(self.repo))
        code, _ = self._gate("mcp__plugin_polymath-vcs_github__push_files")
        self.assertEqual(code, 0)


class ToolPolicyTests(PipelineTestCase):
    def _overlay(self, content: str) -> None:
        (self.repo / ".polymath" / "tool-policy.json").write_text(content)

    def test_base_policy_file_matches_code_fallback(self) -> None:
        path = REPO_ROOT / "plugins" / "polymath-pipeline" / "data" / "tool-policy.json"
        doc = json.loads(path.read_text())
        for key, want in self.mod.TOOL_POLICY_FALLBACK.items():
            self.assertEqual(doc.get(key), want, f"data/tool-policy.json drifted on {key}")

    def test_overlay_strengthens_bash_and_tools(self) -> None:
        self._write_project("enforce")
        self._overlay(json.dumps({
            "bashModifyPatterns": [r"\bmycorptool\b"],
            "gatedTools": ["WebFetch"],
        }))
        policy = self.mod.load_tool_policy(self.repo)
        self.assertTrue(self.mod.bash_is_mutating("mycorptool sync", policy["bash_res"]))
        self.assertIn("WebFetch", policy["gated_tools"])
        payload = {"session_id": "s", "cwd": str(self.repo), "tool_name": "WebFetch", "tool_input": {}}
        code, _, _ = self._hook("hook-pretool", payload)
        self.assertEqual(code, 2)

    def test_overlay_cannot_weaken(self) -> None:
        self._write_project("enforce")
        self._overlay(json.dumps({"mcpReadOnlyVerbs": ["push"], "bashModifyPatterns": []}))
        policy = self.mod.load_tool_policy(self.repo)
        self.assertTrue(self.mod.mcp_is_gated("mcp__x__push_files", policy))
        self.assertTrue(self.mod.bash_is_mutating("rm -rf build", policy["bash_res"]))
        self.assertIn("policy-overlay-ignored", self._events())

    def test_invalid_overlay_keeps_base_policy(self) -> None:
        self._write_project("enforce")
        self._overlay("not json {")
        payload = {"session_id": "s", "cwd": str(self.repo), "tool_name": "Edit", "tool_input": {}}
        code, _, _ = self._hook("hook-pretool", payload)
        self.assertEqual(code, 2)
        self.assertIn("policy-overlay-invalid", self._events())

    def test_hooks_matcher_covers_task_and_mcp(self) -> None:
        hooks = json.loads(
            (REPO_ROOT / "plugins" / "polymath-pipeline" / "hooks" / "hooks.json").read_text()
        )
        matcher = hooks["hooks"]["PreToolUse"][0]["matcher"]
        for needle in ("Bash", "Edit", "Write", "Task", "mcp__"):
            self.assertIn(needle, matcher)


class ClassifyHookTests(PipelineTestCase):
    def test_silent_when_mode_hint_or_absent(self) -> None:
        self._write_project(None)
        code, out, _ = self._hook("hook-prompt", {"session_id": "s", "cwd": str(self.repo)})
        self.assertEqual((code, out), (0, ""))

    def test_directive_emitted_then_silent_after_mark(self) -> None:
        self._write_project("classify")
        payload = {"session_id": "s", "cwd": str(self.repo)}
        code, out, _ = self._hook("hook-prompt", payload)
        self.assertEqual(code, 0)
        self.assertIn("routing.mode=classify", out)
        self.assertIn("[polymath-core route] hint appears above, it has precedence", out)
        self.assertIn("auto-headless", out)
        # mark, then the next prompt is quiet
        rc = self._mark("--surface", "direct", "--cwd", str(self.repo))
        self.assertEqual(rc, 0)
        code, out, _ = self._hook("hook-prompt", payload)
        self.assertEqual((code, out), (0, ""))
        self.assertIn("classify-directive", self._events())
        self.assertIn("classified", self._events())

    def test_kill_switch_is_audited_and_silent(self) -> None:
        self._write_project("classify")
        os.environ["POLYMATH_PIPELINE_OFF"] = "1"
        code, out, _ = self._hook("hook-prompt", {"session_id": "s", "cwd": str(self.repo)})
        self.assertEqual((code, out), (0, ""))
        self.assertIn("kill-switch", self._events())

    def test_malformed_payload_fails_open(self) -> None:
        self._write_project("classify")
        out = io.StringIO()
        prev_stdin = self.mod.sys.stdin
        self.mod.sys.stdin = io.StringIO("this is not json")
        try:
            with redirect_stdout(out):
                code = self.mod.main(["hook-prompt"])
        finally:
            self.mod.sys.stdin = prev_stdin
        self.assertEqual(code, 0)


class EnforceGateTests(PipelineTestCase):
    def _gate(self, tool: str, command: str | None = None, session: str = "s") -> tuple[int, str]:
        payload: dict = {"session_id": session, "cwd": str(self.repo), "tool_name": tool}
        payload["tool_input"] = {"command": command} if command is not None else {}
        code, _, err = self._hook("hook-pretool", payload)
        return code, err

    def test_inactive_outside_enforce(self) -> None:
        self._write_project("classify")
        code, _ = self._gate("Edit")
        self.assertEqual(code, 0)

    def test_read_only_bash_exempt_mutating_denied(self) -> None:
        self._write_project("enforce")
        code, _ = self._gate("Bash", "git status --short")
        self.assertEqual(code, 0)
        code, err = self._gate("Bash", "rm -rf build")
        self.assertEqual(code, 2)
        self.assertIn("classify first", err.lower())
        self.assertIn("enforce-deny", self._events())

    def test_edit_denied_until_marked_then_allowed(self) -> None:
        self._write_project("enforce")
        code, _ = self._gate("Edit")
        self.assertEqual(code, 2)
        self._mark("--surface", "polymath-engineering:feature-dev", "--cwd", str(self.repo))
        code, _ = self._gate("Edit")
        self.assertEqual(code, 0)

    def test_stale_classification_denies_again(self) -> None:
        self._write_project("enforce")
        self._mark("--surface", "direct", "--cwd", str(self.repo))
        # Age the classification past the TTL by rewriting its timestamp.
        markers = list((self.base / ".pdata" / "markers").glob("*.json"))
        self.assertEqual(len(markers), 1)
        doc = json.loads(markers[0].read_text())
        doc["classified_at"] = "2020-01-01T00:00:00+00:00"
        markers[0].write_text(json.dumps(doc))
        code, _ = self._gate("Edit")
        self.assertEqual(code, 2)

    def test_kill_switch_allows_and_audits(self) -> None:
        self._write_project("enforce")
        (self.repo / ".polymath" / "pipeline-off").write_text("")
        code, _ = self._gate("Edit")
        self.assertEqual(code, 0)
        self.assertIn("kill-switch", self._events())

    def test_ungated_tool_allowed(self) -> None:
        self._write_project("enforce")
        code, _ = self._gate("Read")
        self.assertEqual(code, 0)


class MarkerAndSweepTests(PipelineTestCase):
    def test_root_change_invalidates_classification(self) -> None:
        self._write_project("classify")
        marker = self.mod.touch_marker("s", self.repo, "classify")
        self.mod.mark_classified(self.repo, "direct")
        other = self.base / "other"
        (other / ".polymath").mkdir(parents=True)
        refreshed = self.mod.touch_marker("s", other, "classify")
        self.assertNotIn("classified_at", refreshed)

    def test_mark_creates_marker_when_none_exists(self) -> None:
        self._write_project("enforce")
        marker = self.mod.mark_classified(self.repo, "direct")
        self.assertIsNotNone(marker)
        self.assertTrue(str(marker["session"]).startswith("cli-"))
        self.assertIsNotNone(self.mod.fresh_classification("any-session", self.repo))

    def test_sweep_prunes_old_markers_and_truncates_log(self) -> None:
        self._write_project("classify")
        self.mod.touch_marker("old", self.repo, "classify")
        old_path = self.base / ".pdata" / "markers" / "old.json"
        eight_days = 8 * 24 * 3600
        os.utime(old_path, (old_path.stat().st_atime - eight_days, old_path.stat().st_mtime - eight_days))
        self.mod.touch_marker("new", self.repo, "classify")
        log = self.base / ".pdata" / "decisions.jsonl"
        log.write_text('{"ts":"x","event":"filler"}\n' * 30000)
        result = self.mod.sweep()
        self.assertEqual(result["markers_removed"], 1)
        self.assertTrue(result["log_truncated"])
        self.assertFalse(old_path.exists())
        self.assertTrue((self.base / ".pdata" / "markers" / "new.json").exists())
        self.assertLessEqual(len(log.read_text().splitlines()), self.mod.LOG_KEEP_LINES + 1)


class SessionStartTests(PipelineTestCase):
    def test_announces_active_mode(self) -> None:
        self._write_project("enforce")
        code, out, _ = self._hook("hook-session-start", {"session_id": "s", "cwd": str(self.repo)})
        self.assertEqual(code, 0)
        self.assertIn("routing.mode=enforce active", out)

    def test_silent_for_zero_config(self) -> None:
        bare = self.base / "bare"
        (bare / ".git").mkdir(parents=True)
        code, out, _ = self._hook("hook-session-start", {"session_id": "s", "cwd": str(bare)})
        self.assertEqual((code, out), (0, ""))


if __name__ == "__main__":
    unittest.main()
