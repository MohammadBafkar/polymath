"""Unit tests for tools/lib/frontmatter.py.

Covers the documented contract: no frontmatter, unterminated fence,
closing fence at end-of-file, non-mapping frontmatter, unparseable
frontmatter (PyYAML path), and yaml-ish key: value parsing without
PyYAML (the fallback shim path, forced by patching yamlshim.yaml).

Run with: python3 -m unittest discover -s tests/tools
"""

from __future__ import annotations

import pathlib
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.lib import yamlshim  # noqa: E402
from tools.lib.frontmatter import parse_frontmatter  # noqa: E402


class ParseFrontmatterTests(unittest.TestCase):
    def test_well_formed(self) -> None:
        text = "---\nname: prd\ndescription: Draft a PRD\n---\nBody line.\n"
        meta, body = parse_frontmatter(text)
        self.assertEqual(meta, {"name": "prd", "description": "Draft a PRD"})
        self.assertEqual(body, "Body line.\n")

    def test_no_frontmatter_returns_whole_text_as_body(self) -> None:
        text = "# Just a heading\n\nNo fences here.\n"
        self.assertEqual(parse_frontmatter(text), ({}, text))

    def test_fence_not_at_byte_zero_is_no_frontmatter(self) -> None:
        text = "\n---\nname: x\n---\nbody\n"
        self.assertEqual(parse_frontmatter(text), ({}, text))

    def test_unterminated_fence_returns_whole_text_as_body(self) -> None:
        text = "---\nname: x\ndescription: never closed\n"
        self.assertEqual(parse_frontmatter(text), ({}, text))

    def test_closing_fence_at_end_of_file(self) -> None:
        meta, body = parse_frontmatter("---\nname: x\n---")
        self.assertEqual(meta, {"name": "x"})
        self.assertEqual(body, "")

    def test_trailing_whitespace_on_fences_tolerated(self) -> None:
        meta, body = parse_frontmatter("---  \nname: x\n---\t\nbody\n")
        self.assertEqual(meta, {"name": "x"})
        self.assertEqual(body, "body\n")

    def test_body_blank_lines_preserved(self) -> None:
        _, body = parse_frontmatter("---\nname: x\n---\n\n\nbody\n")
        self.assertEqual(body, "\n\nbody\n")

    def test_list_valued_fields(self) -> None:
        text = (
            "---\n"
            "plugin: polymath-product\n"
            "trigger_prompts:\n"
            '  - "draft a PRD"\n'
            "  - 'product spec please'\n"
            "---\n"
        )
        meta, _ = parse_frontmatter(text)
        self.assertEqual(meta["plugin"], "polymath-product")
        self.assertEqual(meta["trigger_prompts"], ["draft a PRD", "product spec please"])

    def test_non_mapping_frontmatter_reads_empty(self) -> None:
        meta, body = parse_frontmatter("---\n- just\n- a list\n---\nbody\n")
        self.assertEqual(meta, {})
        self.assertEqual(body, "body\n")

    @unittest.skipUnless(yamlshim.yaml is not None, "needs PyYAML to raise on bad YAML")
    def test_unparseable_yaml_reads_empty_not_raises(self) -> None:
        meta, body = parse_frontmatter("---\nfoo: [unclosed\n---\nbody\n")
        self.assertEqual(meta, {})
        self.assertEqual(body, "body\n")

    def test_yamlish_lines_parse_without_pyyaml(self) -> None:
        """Force the no-PyYAML path: flat key: value lines must still parse."""
        saved = yamlshim.yaml
        yamlshim.yaml = None
        try:
            text = (
                "---\n"
                "workflow: reviewPlan\n"
                "expect_silent: true\n"
                "must_propose:\n"
                "  - reviewPlan\n"
                "---\n"
                "Why this fixture exists.\n"
            )
            meta, body = parse_frontmatter(text)
            self.assertEqual(meta["workflow"], "reviewPlan")
            self.assertIs(meta["expect_silent"], True)
            self.assertEqual(meta["must_propose"], ["reviewPlan"])
            self.assertEqual(body, "Why this fixture exists.\n")
        finally:
            yamlshim.yaml = saved


if __name__ == "__main__":
    unittest.main()
