"""Unit tests for tools/lib/yamlshim.py.

The fallback parser's documented limitations are CONTRACT, not bugs —
block scalars read as the literal ">"/"|" marker and flow-style mappings
read as strings. These tests pin that behavior (fallback_load_yaml is
called directly so the pins hold whether or not PyYAML is installed) and,
when PyYAML is present, document the divergence on the PyYAML path.

Run with: python3 -m unittest discover -s tests/tools
"""

from __future__ import annotations

import pathlib
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.lib.yamlshim import fallback_load_yaml, load_yaml, yaml  # noqa: E402


class FallbackLoadYamlTests(unittest.TestCase):
    def test_flat_scalars_with_quotes(self) -> None:
        data = fallback_load_yaml('plugin: polymath-product\nskill: "prd"\nname: \'x\'\n')
        self.assertEqual(data, {"plugin": "polymath-product", "skill": "prd", "name": "x"})

    def test_booleans_read_as_bool(self) -> None:
        data = fallback_load_yaml("expect_silent: true\nother: False\n")
        self.assertIs(data["expect_silent"], True)
        self.assertIs(data["other"], False)

    def test_numbers_stay_strings(self) -> None:
        # The shim does no numeric conversion — kept from the originals.
        self.assertEqual(fallback_load_yaml("count: 3\n"), {"count": "3"})

    def test_list_under_key(self) -> None:
        data = fallback_load_yaml(
            "must_invoke:\n"
            "  - polymath-product:prd\n"
            '  - "polymath-thinking:*"\n'
        )
        self.assertEqual(
            data["must_invoke"], ["polymath-product:prd", "polymath-thinking:*"]
        )

    def test_empty_value_key_reads_as_empty_list(self) -> None:
        self.assertEqual(fallback_load_yaml("triggers:\n"), {"triggers": []})

    def test_comments_and_blank_lines_skipped(self) -> None:
        data = fallback_load_yaml("# header\n\nplugin: x\n  # indented comment\n")
        self.assertEqual(data, {"plugin": "x"})

    def test_block_scalar_folding_limitation_kept(self) -> None:
        """CONTRACT: `key: >` reads as the literal ">" and the indented
        continuation lines are dropped — NOT folded into one string."""
        data = fallback_load_yaml("summary: >\n  line one\n  line two\nnext: x\n")
        self.assertEqual(data["summary"], ">")
        self.assertEqual(data["next"], "x")
        data = fallback_load_yaml("summary: |\n  literal block\n")
        self.assertEqual(data["summary"], "|")

    def test_flow_style_mapping_reads_as_string(self) -> None:
        """CONTRACT: flow-style collections are not parsed — the value is
        the literal brace string, not a nested mapping."""
        data = fallback_load_yaml("routing: {mode: hint}\n")
        self.assertEqual(data["routing"], "{mode: hint}")
        self.assertNotIsInstance(data["routing"], dict)

    def test_nested_block_mapping_dropped(self) -> None:
        data = fallback_load_yaml("routing:\n  mode: hint\ntop: x\n")
        self.assertEqual(data, {"routing": [], "top": "x"})

    def test_always_returns_dict(self) -> None:
        self.assertEqual(fallback_load_yaml("- a\n- b\n"), {})


@unittest.skipUnless(yaml is not None, "needs PyYAML")
class PyYamlPathTests(unittest.TestCase):
    """Document where the PyYAML path diverges from the fallback."""

    def test_block_scalar_folds(self) -> None:
        self.assertEqual(
            load_yaml("summary: >\n  line one\n  line two\n"),
            {"summary": "line one line two\n"},
        )

    def test_flow_style_mapping_is_real_mapping(self) -> None:
        self.assertEqual(load_yaml("routing: {mode: hint}\n"), {"routing": {"mode": "hint"}})


if __name__ == "__main__":
    unittest.main()
