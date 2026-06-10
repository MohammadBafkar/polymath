"""Unit tests for bin/polymath-flow.

Loaded via importlib because the script has no .py extension and no entry
point. Tests cover:

  - YAML subset parser fallback (PyYAML disabled per-test)
  - Workflow schema validation
  - State transitions (start → next → complete → assert)
  - mustPass checks: fileExists, fileMatches, commandSucceeds,
    stepSummaryMatches

Run with: python3 -m unittest discover -s plugins/polymath-flows/tests
"""

from __future__ import annotations

import importlib.util
import importlib.machinery
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import textwrap
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
FLOW_SCRIPT = REPO_ROOT / "plugins" / "polymath-flows" / "bin" / "polymath-flow"
SHIP_YAML = REPO_ROOT / "plugins" / "polymath-flows" / "workflows" / "shipFeature.yaml"


def _import_flow():
    # The script has no .py extension, so use SourceFileLoader directly.
    loader = importlib.machinery.SourceFileLoader("polymath_flow", str(FLOW_SCRIPT))
    spec = importlib.util.spec_from_loader("polymath_flow", loader)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _with_no_yaml(monkey_globals: dict) -> dict:
    """Return a copy of the module globals with PyYAML disabled by setting
    yaml to None — forces the fallback _load_yaml branch."""
    g = dict(monkey_globals)
    g["yaml"] = None
    return g


class YamlSubsetParserTests(unittest.TestCase):
    """Exercise the fallback YAML parser baked into bin/polymath-flow."""

    def setUp(self) -> None:
        self.mod = _import_flow()

    def test_top_level_mapping(self) -> None:
        text = textwrap.dedent(
            """\
            schemaVersion: 0.1
            name: example
            version: 1.2.3
            description: a one liner
            """
        )
        # Force fallback by calling the fallback loader directly. The script
        # defines _load_yaml regardless; if PyYAML is present, calling it is
        # still a valid integration test.
        data = self.mod._load_yaml(text)
        self.assertEqual(data["schemaVersion"], 0.1)
        self.assertEqual(data["name"], "example")
        self.assertEqual(data["version"], "1.2.3")
        self.assertEqual(data["description"], "a one liner")

    def test_nested_mapping_and_list(self) -> None:
        text = textwrap.dedent(
            """\
            requires:
              plugins:
                - polymath-core
                - polymath-product
            inputs:
              - name: title
                type: string
                required: true
              - name: scope
                type: enum
                values: [small, medium]
                default: small
            """
        )
        data = self.mod._load_yaml(text)
        self.assertEqual(data["requires"]["plugins"], ["polymath-core", "polymath-product"])
        self.assertEqual(len(data["inputs"]), 2)
        self.assertEqual(data["inputs"][0]["name"], "title")
        self.assertIs(data["inputs"][0]["required"], True)
        self.assertEqual(data["inputs"][1]["values"], ["small", "medium"])

    def test_loads_shipfeature_yaml(self) -> None:
        text = SHIP_YAML.read_text()
        data = self.mod._load_yaml(text)
        self.assertEqual(data["name"], "shipFeature")
        self.assertEqual(data["schemaVersion"], 0.1)
        step_ids = [s["id"] for s in data["steps"]]
        self.assertEqual(
            step_ids,
            ["prd", "acceptance", "implement", "review", "verify", "changelog", "pr"],
        )
        mustpass_ids = [c["id"] for c in data["mustPass"]]
        self.assertIn("prd-exists", mustpass_ids)
        self.assertIn("tests-mentioned", mustpass_ids)

    def test_comments_are_stripped(self) -> None:
        text = textwrap.dedent(
            """\
            # leading comment
            schemaVersion: 0.1   # trailing comment
            name: x
            """
        )
        data = self.mod._load_yaml(text)
        self.assertEqual(data["schemaVersion"], 0.1)
        self.assertEqual(data["name"], "x")

    def test_quoted_list_item_with_colon_under_fallback(self) -> None:
        # Force the homegrown parser (yaml import absent) and confirm a quoted
        # scalar list item containing a colon (e.g. "input:incidentId", used by
        # several workflows' detectionSignals) is NOT misparsed as an inline
        # mapping. Guards the degraded (no-PyYAML) path even though CI has PyYAML.
        saved = sys.modules.get("yaml", "__absent__")
        sys.modules["yaml"] = None  # makes `import yaml` raise ImportError
        try:
            loader = importlib.machinery.SourceFileLoader("pf_noyaml", str(FLOW_SCRIPT))
            spec = importlib.util.spec_from_loader("pf_noyaml", loader)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            got = mod._load_yaml('a:\n  intents:\n    - "input:incidentId"\n    - retro\n')
        finally:
            if saved == "__absent__":
                sys.modules.pop("yaml", None)
            else:
                sys.modules["yaml"] = saved
        self.assertEqual(got, {"a": {"intents": ["input:incidentId", "retro"]}})


class SchemaValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _import_flow()

    def test_shipfeature_validates(self) -> None:
        data = self.mod._load_yaml(SHIP_YAML.read_text())
        self.assertEqual(self.mod._validate(data), [])

    def test_unknown_top_level_key_rejected(self) -> None:
        data = {
            "schemaVersion": 0.1,
            "name": "foo",
            "version": "0.1.0",
            "steps": [{"id": "s1", "invoke": "p:s", "prompt": "p"}],
            "unknownKey": "bad",
        }
        errs = self.mod._validate(data)
        self.assertTrue(any("unknown top-level keys" in e for e in errs))

    def test_unknown_step_key_rejected(self) -> None:
        data = {
            "schemaVersion": 0.1,
            "name": "foo",
            "version": "0.1.0",
            "steps": [
                {"id": "s1", "invoke": "p:c", "prompt": "p", "parallel": True},
            ],
        }
        errs = self.mod._validate(data)
        self.assertTrue(any("unknown keys" in e for e in errs))

    def test_topology_series_and_fanout_accepted(self) -> None:
        for topology in ("series", "fanout"):
            data = {
                "schemaVersion": 0.1,
                "name": "foo",
                "version": "0.1.0",
                "steps": [
                    {"id": "s1", "invoke": "p:c", "prompt": "p", "topology": topology},
                ],
            }
            errs = self.mod._validate(data)
            self.assertEqual(errs, [], f"topology={topology} unexpectedly rejected: {errs}")

    def test_topology_unknown_value_rejected(self) -> None:
        data = {
            "schemaVersion": 0.1,
            "name": "foo",
            "version": "0.1.0",
            "steps": [
                {"id": "s1", "invoke": "p:c", "prompt": "p", "topology": "debate"},
            ],
        }
        errs = self.mod._validate(data)
        self.assertTrue(any("topology" in e for e in errs))

    def test_unsupported_schema_version_rejected(self) -> None:
        data = {"schemaVersion": 0.2, "name": "foo", "version": "0.1.0", "steps": []}
        errs = self.mod._validate(data)
        self.assertTrue(any("unsupported schemaVersion" in e for e in errs))

    def test_duplicate_step_id_rejected(self) -> None:
        data = {
            "schemaVersion": 0.1,
            "name": "foo",
            "version": "0.1.0",
            "steps": [
                {"id": "s1", "invoke": "p:c", "prompt": "p"},
                {"id": "s1", "invoke": "p:d", "prompt": "p"},
            ],
        }
        errs = self.mod._validate(data)
        self.assertTrue(any("duplicate" in e for e in errs))


_PRD_FRONTMATTER = (
    "artifact: PRD\n"
    "schemaVersion: 0.1\n"
    'title: "{title}"\n'
    "status: draft\n"
    "owner: pmteam\n"
    'created: "2026-05-24"\n'
)
_PRD_BODY = (
    "## Problem\n"
    "The login endpoint accepts unlimited attempts per IP per minute, which "
    "lets credential-stuffing actors enumerate accounts faster than "
    "downstream rate limits can catch.\n\n"
    "## Goal\n"
    "Cap unauthenticated login attempts to ten per IP per minute, returning "
    "HTTP 429 once exceeded. The cap must be observable in metrics and "
    "reversible via feature flag within sixty seconds.\n\n"
    "## Acceptance criteria\n"
    "- Given an IP under ten attempts in a minute, when it posts to /login, "
    "then the response status is whatever the credentials warrant.\n"
    "- Given an IP at the cap, when it posts again, then the response is 429.\n"
)


def _write_real_prd(path: pathlib.Path, title: str) -> None:
    body = "---\n" + _PRD_FRONTMATTER.format(title=title) + "---\n" + _PRD_BODY
    path.write_text(body)


def _git(*args: str, cwd: pathlib.Path) -> None:
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "Test",
        "GIT_AUTHOR_EMAIL": "test@example.com",
        "GIT_COMMITTER_NAME": "Test",
        "GIT_COMMITTER_EMAIL": "test@example.com",
    }
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, env=env)


class StateTransitionTests(unittest.TestCase):
    """End-to-end through the public CLI surface in a tmpdir + scratch repo."""

    def setUp(self) -> None:
        self.mod = _import_flow()
        self._tmp = tempfile.TemporaryDirectory()
        self.work = pathlib.Path(self._tmp.name)
        self._prev_data = os.environ.get("CLAUDE_PLUGIN_DATA")
        os.environ["CLAUDE_PLUGIN_DATA"] = str(self.work / ".pdata")
        self._prev_cwd = pathlib.Path.cwd()
        os.chdir(self.work)
        # Initialize a git repo with a baseline commit so diffConstraint can
        # observe real changes against HEAD.
        _git("init", "-q", cwd=self.work)
        (self.work / "README.md").write_text("# Scratch repo for tests\n")
        _git("add", "README.md", cwd=self.work)
        _git("commit", "-q", "-m", "init", cwd=self.work)

    def tearDown(self) -> None:
        os.chdir(self._prev_cwd)
        if self._prev_data is None:
            os.environ.pop("CLAUDE_PLUGIN_DATA", None)
        else:
            os.environ["CLAUDE_PLUGIN_DATA"] = self._prev_data
        self._tmp.cleanup()

    def _capture(self, *argv: str) -> tuple[int, str]:
        from io import StringIO
        from contextlib import redirect_stdout

        buf = StringIO()
        code = 0
        with redirect_stdout(buf):
            try:
                code = self.mod.main(list(argv))
            except SystemExit as e:
                code = int(e.code) if e.code is not None else 0
        return code, buf.getvalue()

    def test_full_shipfeature_walk(self) -> None:
        code, out = self._capture(
            "start", "shipFeature",
            "--input", "title=Rate-limit /login",
            "--input", "scope=small",
        )
        self.assertEqual(code, 0)
        run_id = json.loads(out)["run_id"]

        code, out = self._capture("next", run_id)
        self.assertEqual(code, 0)
        first = json.loads(out)
        self.assertEqual(first["step_id"], "prd")
        self.assertEqual(first["invoke"], "polymath-product:prd")
        self.assertIn("rate-limit-login", first["artifacts"][0])

        steps = ["prd", "acceptance", "implement", "review", "verify", "changelog", "pr"]
        summaries = {
            "prd": "PRD drafted",
            "acceptance": "Acceptance criteria added",
            "implement": "Implementation complete",
            "review": "Reviewed",
            "verify": "All tests verified, ran lint and typecheck",
            "changelog": "CHANGELOG updated",
            "pr": "PR description drafted",
        }

        # Pre-create the artifacts expected by mustPass.
        (self.work / "docs" / "prds").mkdir(parents=True, exist_ok=True)
        (self.work / "docs" / "pr").mkdir(parents=True, exist_ok=True)
        _write_real_prd(
            self.work / "docs" / "prds" / "rate-limit-login.md",
            title="Rate-limit /login",
        )
        (self.work / "CHANGELOG.md").write_text("## [Unreleased]\n- Rate-limit /login\n")
        (self.work / "docs" / "pr" / "rate-limit-login.md").write_text(
            "# PR — Rate-limit /login\n\nImplements the cap described in the PRD.\n"
        )
        # Implement step must produce a real diff to satisfy diffConstraint.
        (self.work / "src").mkdir(parents=True, exist_ok=True)
        (self.work / "src" / "rate_limit.py").write_text(
            "def is_rate_limited(ip: str, attempts: int) -> bool:\n"
            "    return attempts >= 10\n"
        )

        for sid in steps:
            sf = self.work / f"{sid}.summary.md"
            sf.write_text(summaries[sid])
            code, _ = self._capture("complete", run_id, sid, "--summary", str(sf))
            self.assertEqual(code, 0, f"complete step {sid} failed")

        code, out = self._capture("assert", run_id)
        self.assertEqual(code, 0, msg=f"assert failed: {out}")
        result = json.loads(out)
        self.assertEqual(result["status"], "completed")
        # 5 blocking + 1 advisory = 6 total in the migrated shipFeature.
        self.assertEqual(result["checks"], 6)

    def test_assert_pauses_on_missing_artifact(self) -> None:
        code, out = self._capture(
            "start", "shipFeature",
            "--input", "title=feature x",
        )
        run_id = json.loads(out)["run_id"]
        for sid in ["prd", "acceptance", "implement", "review", "verify", "changelog", "pr"]:
            sf = self.work / f"{sid}.summary.md"
            sf.write_text("tests verified")
            self._capture("complete", run_id, sid, "--summary", str(sf))

        code, out = self._capture("assert", run_id)
        self.assertEqual(code, 2)
        result = json.loads(out)
        self.assertEqual(result["status"], "paused")
        ids = {f["id"] for f in result["failures"]}
        # Weak fileExists checks still fail when artifacts are missing.
        self.assertIn("prd-exists", ids)
        self.assertIn("pr-draft-exists", ids)
        # The strong artifact-strict gate also fires because the PRD path
        # doesn't exist at all. diffConstraint behavior is exercised by
        # test_hollow_run_blocked_by_strong_gates.
        self.assertIn("prd-strict", ids)

    def test_stepsummary_matches_is_advisory_by_default(self) -> None:
        """stepSummaryMatches defaults to advisory severity — a failure
        reports as an advisory but does NOT pause the workflow. Only
        strong-deterministic blocking checks (commandSucceeds, artifactValid,
        artifactSchemaStrict, diffConstraint) can pause on their own."""
        code, out = self._capture(
            "start", "shipFeature",
            "--input", "title=keyword check",
        )
        run_id = json.loads(out)["run_id"]
        (self.work / "docs" / "prds").mkdir(parents=True)
        (self.work / "docs" / "pr").mkdir(parents=True)
        _write_real_prd(
            self.work / "docs" / "prds" / "keyword-check.md", title="keyword check"
        )
        (self.work / "CHANGELOG.md").write_text("ok")
        (self.work / "docs" / "pr" / "keyword-check.md").write_text(
            "# PR — keyword check\n\nDoes the thing.\n"
        )
        (self.work / "src").mkdir(parents=True, exist_ok=True)
        (self.work / "src" / "change.py").write_text("x = 1\n")
        for sid in ["prd", "acceptance", "implement", "review", "verify", "changelog", "pr"]:
            sf = self.work / f"{sid}.summary.md"
            # NB: deliberately omit test/verify keywords from the verify step
            sf.write_text("nothing here" if sid == "verify" else "ok")
            self._capture("complete", run_id, sid, "--summary", str(sf))

        code, out = self._capture("assert", run_id)
        self.assertEqual(code, 0)
        result = json.loads(out)
        self.assertEqual(result["status"], "completed")
        advisory_ids = {a["id"] for a in result.get("advisories", [])}
        self.assertIn("tests-mentioned", advisory_ids)

    def test_hollow_run_blocked_by_strong_gates(self) -> None:
        """FALSIFIABILITY ANCHOR for the deterministic-gate hardening.

        Before the v0.2 gate work, a deliberately hollow shipFeature run —
        empty PRD stub (`# PRD\\n`), no real diff in the worktree, but with
        all the required filenames present and the verify summary mentioning
        'tests' — *passed* shipFeature's mustPass checks. That was the
        evidence that 'deterministic enforcement' was marketing rather than
        fact.

        This test asserts the new, hardened contract: such a run is BLOCKED
        by artifactSchemaStrict (PRD stub fails minBodyChars and frontmatter
        requirements) and diffConstraint (filesChanged.min=1 with zero
        changes). The day this test starts failing is the day the gates
        have regressed below the v0.2 bar."""
        code, out = self._capture(
            "start", "shipFeature",
            "--input", "title=hollow",
        )
        run_id = json.loads(out)["run_id"]
        # Create only what the WEAK fileExists checks demand. Bodies are
        # deliberately empty stubs; no source code change is made.
        (self.work / "docs" / "prds").mkdir(parents=True)
        (self.work / "docs" / "pr").mkdir(parents=True)
        (self.work / "docs" / "prds" / "hollow.md").write_text("# PRD\n")
        (self.work / "CHANGELOG.md").write_text("## [Unreleased]\n")
        (self.work / "docs" / "pr" / "hollow.md").write_text("# PR\n")
        for sid in ["prd", "acceptance", "implement", "review", "verify", "changelog", "pr"]:
            sf = self.work / f"{sid}.summary.md"
            sf.write_text("tests verified, all green")  # would match the weak regex
            self._capture("complete", run_id, sid, "--summary", str(sf))

        code, out = self._capture("assert", run_id)
        self.assertEqual(code, 2, msg=f"hollow run unexpectedly passed: {out}")
        result = json.loads(out)
        self.assertEqual(result["status"], "paused")
        failure_ids = {f["id"] for f in result["failures"]}
        # The PRD stub is detected by artifactSchemaStrict (frontmatter
        # missing + body below minBodyChars). This is the load-bearing gate
        # for hollow runs: even if the executor created every other stub the
        # weak fileExists checks expect, the strict artifact check still
        # blocks because the PRD is not a PRD.
        self.assertIn("prd-strict", failure_ids)
        # The weak gates do NOT fail — that's the bug this test exists to
        # prove was real. Files exist, summary mentions tests; only the
        # strong gates can tell the work is hollow.
        weak_ids = {"prd-exists", "pr-draft-exists", "changelog-touched"}
        self.assertFalse(
            weak_ids & failure_ids,
            msg=f"weak gates unexpectedly failed: {weak_ids & failure_ids}",
        )
        # Severity is carried through to the failure record so callers can
        # distinguish strong blockers from advisories.
        prd_failure = next(f for f in result["failures"] if f["id"] == "prd-strict")
        self.assertEqual(prd_failure["severity"], "blocking")
        self.assertEqual(prd_failure["type"], "artifactSchemaStrict")


class ArtifactValidTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _import_flow()
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = pathlib.Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _write(self, fm: str, body: str = "# body\n") -> pathlib.Path:
        p = self.tmp / "Artifact.md"
        p.write_text(f"---\n{fm}\n---\n{body}")
        return p

    def test_prd_valid_frontmatter(self) -> None:
        path = self._write(
            "artifact: PRD\n"
            "schemaVersion: 0.1\n"
            'title: "Rate-limit login"\n'
            "status: draft\n"
            "owner: pmteam\n"
            'created: "2026-05-24"\n'
        )
        ok, detail = self.mod._validate_artifact_frontmatter(str(path), "PRD")
        self.assertTrue(ok, detail)

    def test_prd_missing_required_fields(self) -> None:
        path = self._write(
            "artifact: PRD\n"
            'title: "x"\n'
        )
        ok, detail = self.mod._validate_artifact_frontmatter(str(path), "PRD")
        self.assertFalse(ok)
        self.assertIn("missing required field", detail)

    def test_prd_wrong_status_enum(self) -> None:
        path = self._write(
            "artifact: PRD\n"
            'title: "x"\n'
            "status: bogus\n"
            "owner: x\n"
            'created: "2026-05-24"\n'
        )
        ok, detail = self.mod._validate_artifact_frontmatter(str(path), "PRD")
        self.assertFalse(ok)
        self.assertIn("status", detail)

    def test_adr_accepts_array_or_string_deciders(self) -> None:
        for deciders in ('"alice"', "[alice, bob]"):
            path = self._write(
                "artifact: ADR\n"
                'title: "Use Postgres"\n'
                "status: accepted\n"
                f"deciders: {deciders}\n"
                'date: "2026-05-24"\n'
            )
            ok, detail = self.mod._validate_artifact_frontmatter(str(path), "ADR")
            self.assertTrue(ok, f"deciders={deciders!r}: {detail}")

    def test_postmortem_requires_blameless_true(self) -> None:
        path = self._write(
            "artifact: Postmortem\n"
            'incident_id: "IC-2026-09"\n'
            "severity: sev1\n"
            "status: draft\n"
            'facilitator: "alice"\n'
            'occurred: "2026-05-23T14:00:00Z"\n'
            'resolved: "2026-05-23T16:00:00Z"\n'
            "blameless: false\n"
        )
        ok, detail = self.mod._validate_artifact_frontmatter(str(path), "Postmortem")
        self.assertFalse(ok)
        self.assertIn("blameless", detail)

    def test_threat_model_stride_enum(self) -> None:
        path = self._write(
            "artifact: ThreatModel\n"
            'system: "Login"\n'
            'scope: "Authentication"\n'
            'owner: "secteam"\n'
            'created: "2026-05-24"\n'
            "stride_categories: [Spoofing, BogusCategory]\n"
        )
        ok, detail = self.mod._validate_artifact_frontmatter(str(path), "ThreatModel")
        self.assertFalse(ok)
        self.assertIn("stride_categories", detail)

    def test_missing_frontmatter(self) -> None:
        p = self.tmp / "no-fm.md"
        p.write_text("# Just a heading\nno frontmatter here.\n")
        ok, detail = self.mod._validate_artifact_frontmatter(str(p), "PRD")
        self.assertFalse(ok)
        self.assertIn("missing YAML frontmatter", detail)

    def test_check_artifactvalid_via_runcheck(self) -> None:
        path = self._write(
            "artifact: PRD\n"
            'title: "ok"\n'
            "status: draft\n"
            "owner: pm\n"
            'created: "2026-05-24"\n'
        )
        check = {
            "id": "prd-valid",
            "type": "artifactValid",
            "path": str(path),
            "artifact": "PRD",
        }
        ok, _ = self.mod._run_check(check, self.tmp, {}, {"slug": "x"})
        self.assertTrue(ok)


class ResumabilityTests(unittest.TestCase):
    """Phase 5: last_active tracking, budget-stub removal, gc pruning."""

    def setUp(self) -> None:
        self.mod = _import_flow()
        self._tmp = tempfile.TemporaryDirectory()
        self.work = pathlib.Path(self._tmp.name)
        self._prev_data = os.environ.get("CLAUDE_PLUGIN_DATA")
        os.environ["CLAUDE_PLUGIN_DATA"] = str(self.work / ".pdata")
        self.runs = self.work / ".pdata" / "workflows"
        self._prev_cwd = pathlib.Path.cwd()
        os.chdir(self.work)  # isolate from the repo's own .polymath/

    def tearDown(self) -> None:
        os.chdir(self._prev_cwd)
        if self._prev_data is None:
            os.environ.pop("CLAUDE_PLUGIN_DATA", None)
        else:
            os.environ["CLAUDE_PLUGIN_DATA"] = self._prev_data
        self._tmp.cleanup()

    def _capture(self, *argv: str) -> tuple[int, str]:
        from io import StringIO
        from contextlib import redirect_stdout

        buf = StringIO()
        code = 0
        with redirect_stdout(buf):
            try:
                code = self.mod.main(list(argv))
            except SystemExit as e:
                code = int(e.code) if e.code is not None else 0
        return code, buf.getvalue()

    def _mk_run(self, run_id: str, status: str, days_ago: float) -> None:
        import datetime

        d = self.runs / run_id
        d.mkdir(parents=True, exist_ok=True)
        ts = (
            datetime.datetime.now(datetime.timezone.utc)
            - datetime.timedelta(days=days_ago)
        ).replace(microsecond=0).isoformat()
        (d / "state.json").write_text(
            json.dumps({"run_id": run_id, "workflow": "x", "status": status, "last_active": ts})
        )

    def test_start_writes_last_active_and_no_budget(self) -> None:
        code, out = self._capture(
            "start", "shipFeature", "--input", "title=Demo", "--input", "scope=small"
        )
        self.assertEqual(code, 0)
        run_dir = self.runs / json.loads(out)["run_id"]
        state = json.loads((run_dir / "state.json").read_text())
        self.assertIn("last_active", state)
        self.assertIsNotNone(self.mod._parse_iso(state["last_active"]))
        self.assertFalse((run_dir / "budget.json").exists(), "budget.json stub must not be written")

    def test_gc_prunes_only_old_terminal_runs(self) -> None:
        self._mk_run("old-done", "completed", 40)
        self._mk_run("recent-done", "completed", 1)
        self._mk_run("old-paused", "paused", 90)
        self._mk_run("old-active", "active", 90)
        code, out = self._capture("gc", "--days", "30")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["removed"], ["old-done"])
        self.assertFalse((self.runs / "old-done").exists())
        for keep in ("recent-done", "old-paused", "old-active"):
            self.assertTrue((self.runs / keep).exists(), f"{keep} must survive gc")

    def test_gc_dry_run_does_not_delete(self) -> None:
        self._mk_run("old-done", "completed", 40)
        code, out = self._capture("gc", "--dry-run")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["removed"], ["old-done"])
        self.assertTrue((self.runs / "old-done").exists(), "dry-run must not delete")

    def test_gc_explicit_status_prunes_paused(self) -> None:
        self._mk_run("old-paused", "paused", 90)
        code, out = self._capture("gc", "--status", "paused", "--days", "30")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["removed"], ["old-paused"])
        self.assertFalse((self.runs / "old-paused").exists())

    def test_inflight_marker_set_by_next_cleared_by_complete(self) -> None:
        code, out = self._capture("start", "shipFeature", "--input", "title=Demo", "--input", "scope=small")
        self.assertEqual(code, 0)
        run_id = json.loads(out)["run_id"]
        sd = self.runs / run_id
        # `next` marks the issued step in-flight.
        code, out = self._capture("next", run_id)
        self.assertEqual(code, 0)
        step_id = json.loads(out)["step_id"]
        state = json.loads((sd / "state.json").read_text())
        self.assertIsNotNone(state.get("in_flight"))
        self.assertEqual(state["in_flight"]["step"], step_id)
        # `checkpoint` annotates the in-flight step.
        code, _ = self._capture("checkpoint", run_id, "--note", "halfway")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads((sd / "state.json").read_text())["in_flight"]["note"], "halfway")
        # `complete` clears the in-flight breadcrumb.
        code, _ = self._capture("complete", run_id, step_id, "--summary", "done")
        self.assertEqual(code, 0)
        self.assertIsNone(json.loads((sd / "state.json").read_text()).get("in_flight"))

    def test_chainsto_surfaced_on_completion(self) -> None:
        import contextlib
        import io

        run_dir = self.runs / "chain-run"
        run_dir.mkdir(parents=True)
        (run_dir / "state.json").write_text(json.dumps({"run_id": "chain-run", "status": "active", "steps": []}))
        workflow = {"name": "x", "chainsTo": ["incidentRetroToActions"]}  # no mustPass -> immediate completion
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = self.mod._assert(run_dir, workflow, {}, {"slug": "x"})
        out = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(out["status"], "completed")
        self.assertEqual(out["chainsTo"], ["incidentRetroToActions"])


class ProjectPlaceholderTests(unittest.TestCase):
    """${project.*} placeholders: lookup, fallback form, snapshot resolution,
    freeze-at-start, and the bare-form validate warning."""

    SNAPSHOT = {
        "schemaVersion": 1,
        "project": {"name": "demo"},
        "stack": {"languages": [{"lang": "go", "version": "1.22"}]},
        "conventions": {"commit_style": "conventional-commits"},
    }

    def setUp(self) -> None:
        self.mod = _import_flow()
        self._tmp = tempfile.TemporaryDirectory()
        self.work = pathlib.Path(self._tmp.name)
        self._prev_data = os.environ.get("CLAUDE_PLUGIN_DATA")
        os.environ["CLAUDE_PLUGIN_DATA"] = str(self.work / ".pdata")

    def tearDown(self) -> None:
        if self._prev_data is None:
            os.environ.pop("CLAUDE_PLUGIN_DATA", None)
        else:
            os.environ["CLAUDE_PLUGIN_DATA"] = self._prev_data
        self._tmp.cleanup()

    def _sub(self, text: str, project: dict | None) -> str:
        return self.mod._substitute(
            text, inputs={}, workflow_meta={}, project=project
        )

    def test_dotted_path_with_list_index(self) -> None:
        out = self._sub("lang=${project.stack.languages.0.lang}", self.SNAPSHOT)
        self.assertEqual(out, "lang=go")

    def test_mapping_value_json_encodes(self) -> None:
        out = self._sub("${project.project}", self.SNAPSHOT)
        self.assertEqual(out, '{"name":"demo"}')

    def test_bare_miss_stays_literal(self) -> None:
        out = self._sub("x ${project.nope.deep} y", self.SNAPSHOT)
        self.assertEqual(out, "x ${project.nope.deep} y")

    def test_bare_form_without_snapshot_stays_literal(self) -> None:
        out = self._sub("x ${project.project.name} y", None)
        self.assertEqual(out, "x ${project.project.name} y")

    def test_fallback_used_on_miss_and_when_no_snapshot(self) -> None:
        self.assertEqual(self._sub("${project.nope:-deft}", self.SNAPSHOT), "deft")
        self.assertEqual(self._sub("${project.project.name:-deft}", None), "deft")

    def test_fallback_ignored_on_hit(self) -> None:
        out = self._sub("${project.project.name:-deft}", self.SNAPSHOT)
        self.assertEqual(out, "demo")

    def _write_snapshot(self, rel: str, payload: dict) -> pathlib.Path:
        p = self.work / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(payload))
        return p

    def test_snapshot_resolved_from_env_data_dir(self) -> None:
        self._write_snapshot(".pdata/polymath-core/project-context.json", self.SNAPSHOT)
        snap = self.mod._project_context_snapshot()
        self.assertIsNotNone(snap)
        self.assertEqual(snap["project"]["name"], "demo")

    def test_snapshot_resolved_from_marketplace_namespaced_sibling(self) -> None:
        # polymath-core's data dir is a SIBLING of this plugin's data dir
        # (per-plugin+marketplace namespacing): data/<plugin>-<marketplace>/.
        self._write_snapshot(
            "polymath-core-somemkt/polymath-core/project-context.json", self.SNAPSHOT
        )
        snap = self.mod._project_context_snapshot()
        self.assertIsNotNone(snap)
        self.assertEqual(snap["project"]["name"], "demo")

    def test_newest_snapshot_wins(self) -> None:
        old = self._write_snapshot(
            ".pdata/polymath-core/project-context.json",
            {**self.SNAPSHOT, "project": {"name": "stale"}},
        )
        os.utime(old, (1, 1))
        self._write_snapshot(
            "polymath-core-somemkt/polymath-core/project-context.json", self.SNAPSHOT
        )
        snap = self.mod._project_context_snapshot()
        self.assertEqual(snap["project"]["name"], "demo")

    def test_missing_snapshot_returns_none(self) -> None:
        self.assertIsNone(self.mod._project_context_snapshot())

    def test_start_freezes_snapshot_into_state(self) -> None:
        self._write_snapshot(".pdata/polymath-core/project-context.json", self.SNAPSHOT)
        prev_cwd = pathlib.Path.cwd()
        os.chdir(self.work)
        try:
            from io import StringIO
            from contextlib import redirect_stdout

            buf = StringIO()
            with redirect_stdout(buf):
                code = self.mod.main(
                    ["start", "shipFeature", "--input", "title=Freeze test",
                     "--input", "scope=small"]
                )
            self.assertEqual(code, 0)
            run_id = json.loads(buf.getvalue())["run_id"]
            state = json.loads(
                (self.mod._workflow_runs_dir() / run_id / "state.json").read_text()
            )
            self.assertEqual(
                state["project_context"]["project"]["name"], "demo"
            )
        finally:
            os.chdir(prev_cwd)

    def test_bare_placeholder_warning(self) -> None:
        wf = {
            "steps": [
                {"id": "a", "prompt": "use ${project.stack.languages.0.lang}",
                 "artifacts": []}
            ],
            "mustPass": [],
        }
        warn = self.mod._bare_project_placeholder_warning(wf)
        self.assertIsNotNone(warn)
        self.assertIn("steps.a.prompt", warn)

    def test_fallback_form_produces_no_warning(self) -> None:
        wf = {
            "steps": [
                {"id": "a", "prompt": "use ${project.x:-none}", "artifacts": []}
            ],
            "mustPass": [{"id": "c", "type": "fileExists",
                          "path": "${project.y:-docs/out.md}"}],
        }
        self.assertIsNone(self.mod._bare_project_placeholder_warning(wf))


if __name__ == "__main__":
    unittest.main()
