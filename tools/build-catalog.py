#!/usr/bin/env python3
"""Generate docs/site/ — the GitHub Pages catalog.

Reads .claude-plugin/marketplace.json and each plugin's README.md and
plugin.json, then writes:
  docs/site/index.html            — landing page with category groupings
  docs/site/plugins/<name>.html   — one detail page per plugin
  docs/site/assets/style.css      — minimal stylesheet

No external dependencies. Plain HTML + a tiny stylesheet so the site stays
trivial to host (GitHub Pages, Vercel, anywhere).

Usage:
  tools/build-catalog.py            # write under docs/site/
  tools/build-catalog.py --check    # exit non-zero if regeneration would change files
"""

from __future__ import annotations

import argparse
import html
import json
import pathlib
import re
import sys
import textwrap


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE_DIR = REPO_ROOT / "docs" / "site"
MARKETPLACE_JSON = REPO_ROOT / ".claude-plugin" / "marketplace.json"


CATEGORY_ORDER = [
    "foundation",
    "product",
    "engineering",
    "languages",
    "release",
    "orchestration",
    "thinking",
    "planning",
    "writing",
    "quality",
    "security",
    "platform",
    "devops",
    "infra",
    "sre",
    "observability",
    "incident",
    "data",
    "ai",
    "connector",
    "author",
]


def load_marketplace() -> dict:
    return json.loads(MARKETPLACE_JSON.read_text())


def plugin_readme(plugin_dir: pathlib.Path) -> str:
    readme = plugin_dir / "README.md"
    if not readme.exists():
        return ""
    return readme.read_text()


def md_to_html_minimal(md: str) -> str:
    """Rough Markdown→HTML conversion. Good enough for plugin READMEs."""
    out_lines: list[str] = []
    in_code = False
    in_list = False
    for raw_line in md.splitlines():
        line = raw_line
        if line.startswith("```"):
            if in_code:
                out_lines.append("</code></pre>")
                in_code = False
            else:
                out_lines.append('<pre><code>')
                in_code = True
            continue
        if in_code:
            out_lines.append(html.escape(line))
            continue
        stripped = line.strip()
        # headings
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            if in_list:
                out_lines.append("</ul>")
                in_list = False
            level = len(m.group(1))
            out_lines.append(f"<h{level}>{html.escape(m.group(2))}</h{level}>")
            continue
        # list items
        if stripped.startswith("- "):
            if not in_list:
                out_lines.append("<ul>")
                in_list = True
            item = stripped[2:]
            item = render_inline(item)
            out_lines.append(f"<li>{item}</li>")
            continue
        # blank line
        if not stripped:
            if in_list:
                out_lines.append("</ul>")
                in_list = False
            out_lines.append("")
            continue
        # default paragraph
        if in_list:
            out_lines.append("</ul>")
            in_list = False
        out_lines.append(f"<p>{render_inline(stripped)}</p>")
    if in_list:
        out_lines.append("</ul>")
    if in_code:
        out_lines.append("</code></pre>")
    return "\n".join(out_lines)


def render_inline(text: str) -> str:
    text = html.escape(text)
    # links [a](b)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    # inline code
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    # bold
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    return text


PAGE_SHELL = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <link rel="stylesheet" href="{root}assets/style.css">
</head>
<body>
  <header>
    <h1><a href="{root}index.html">Polymath marketplace</a></h1>
    <p class="tagline">A public, open-source Claude Code marketplace of work-shaped plugins.</p>
  </header>
  <main>
{body}
  </main>
  <footer>
    <p>Apache-2.0 · <a href="https://github.com/MohammadBafkar/Polymath">Source</a> · Generated from <code>.claude-plugin/marketplace.json</code></p>
  </footer>
</body>
</html>
"""


STYLE = """:root {
  --bg: #ffffff;
  --fg: #1a1a1a;
  --muted: #586069;
  --accent: #0366d6;
  --border: #e1e4e8;
  --code-bg: #f6f8fa;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0d1117;
    --fg: #c9d1d9;
    --muted: #8b949e;
    --accent: #58a6ff;
    --border: #30363d;
    --code-bg: #161b22;
  }
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  color: var(--fg);
  background: var(--bg);
  line-height: 1.5;
}
header, main, footer { max-width: 980px; margin: 0 auto; padding: 1.5rem 1rem; }
header { border-bottom: 1px solid var(--border); }
header h1 { margin: 0 0 .25rem; font-size: 1.6rem; }
header h1 a { color: var(--fg); text-decoration: none; }
.tagline { margin: 0; color: var(--muted); }
footer { border-top: 1px solid var(--border); color: var(--muted); font-size: .9rem; }
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
h2 { margin-top: 2rem; padding-bottom: .25rem; border-bottom: 1px solid var(--border); }
.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem; }
.card {
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 1rem;
  background: var(--bg);
}
.card h3 { margin: 0 0 .5rem; font-size: 1.05rem; }
.card h3 a { color: var(--fg); }
.card p { margin: 0; color: var(--muted); font-size: .92rem; }
.tags { margin-top: .5rem; font-size: .8rem; color: var(--muted); }
.tags span {
  display: inline-block;
  padding: .1rem .4rem;
  border: 1px solid var(--border);
  border-radius: 999px;
  margin-right: .25rem;
  margin-bottom: .25rem;
}
pre, code {
  font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  font-size: .88em;
}
pre {
  background: var(--code-bg);
  padding: .75rem 1rem;
  border-radius: 6px;
  overflow-x: auto;
}
code { background: var(--code-bg); padding: .1em .35em; border-radius: 3px; }
pre code { background: none; padding: 0; }
.plugin-meta { color: var(--muted); font-size: .92rem; margin-top: -0.5rem; }
.status {
  font-size: .65rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .04em;
  padding: .1rem .4rem;
  border-radius: 3px;
  vertical-align: middle;
  margin-left: .35rem;
}
.status-stable { background: #1f6f43; color: #fff; }
.status-experimental { background: #d68427; color: #fff; }
.status-beta { background: #4a6fa5; color: #fff; }
.status-deprecated { background: #6b6b6b; color: #fff; }
"""


def write_if_changed(path: pathlib.Path, content: str, check: bool) -> bool:
    """Return True iff content differs from existing file."""
    existing = path.read_text() if path.exists() else None
    if existing == content:
        return False
    if not check:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    return True


def build(check: bool) -> int:
    marketplace = load_marketplace()
    plugins = marketplace.get("plugins", [])
    grouped: dict[str, list[dict]] = {}
    for p in plugins:
        cat = p.get("category", "uncategorized")
        grouped.setdefault(cat, []).append(p)

    diffs: list[pathlib.Path] = []

    # 1. CSS
    css_path = SITE_DIR / "assets" / "style.css"
    if write_if_changed(css_path, STYLE, check):
        diffs.append(css_path)

    # 2. Index page
    sections_html = []
    sections_html.append(
        '<h2>Install the marketplace</h2>\n'
        '<pre><code>claude plugin marketplace add https://github.com/MohammadBafkar/Polymath</code></pre>'
    )
    sections_html.append(
        f'<p class="plugin-meta">{len(plugins)} plugins · '
        f'Apache-2.0 · '
        f'<a href="https://github.com/MohammadBafkar/Polymath">Source on GitHub</a></p>'
    )

    seen_cats: set[str] = set()
    order = CATEGORY_ORDER + sorted(c for c in grouped if c not in CATEGORY_ORDER)
    for cat in order:
        if cat not in grouped or cat in seen_cats:
            continue
        seen_cats.add(cat)
        sections_html.append(f'<h2 id="cat-{html.escape(cat)}">{html.escape(cat.title())}</h2>')
        cards = ['<div class="cards">']
        for p in sorted(grouped[cat], key=lambda x: x["name"]):
            name = p["name"]
            status = p.get("status", "experimental")
            cards.append('<div class="card">')
            badge = (
                f'<span class="status status-{html.escape(status)}">{html.escape(status)}</span>'
            )
            cards.append(
                f'<h3><a href="plugins/{html.escape(name)}.html">{html.escape(name)}</a> {badge}</h3>'
            )
            cards.append(f'<p>{html.escape(p.get("description",""))}</p>')
            tags = p.get("tags", [])
            if tags:
                tag_spans = "".join(f"<span>{html.escape(t)}</span>" for t in tags)
                cards.append(f'<div class="tags">{tag_spans}</div>')
            cards.append("</div>")
        cards.append("</div>")
        sections_html.append("\n".join(cards))

    index_path = SITE_DIR / "index.html"
    index_html = PAGE_SHELL.format(
        title="Polymath marketplace",
        root="",
        body="\n".join(sections_html),
    )
    if write_if_changed(index_path, index_html, check):
        diffs.append(index_path)

    # 3. Per-plugin pages
    for p in plugins:
        plugin_dir = REPO_ROOT / p["source"].lstrip("./")
        manifest = plugin_dir / ".claude-plugin" / "plugin.json"
        readme_md = plugin_readme(plugin_dir)
        readme_html = md_to_html_minimal(readme_md) if readme_md else "<p><em>README not present.</em></p>"
        details_extra = ""
        if manifest.exists():
            data = json.loads(manifest.read_text())
            details_extra = (
                f'<p class="plugin-meta">version {html.escape(data.get("version","?"))} · '
                f'{html.escape(data.get("license","?"))} · '
                f'dependencies: {html.escape(", ".join(data.get("dependencies") or []) or "—")}</p>'
            )
        body = (
            f'<p><a href="../index.html">← all plugins</a></p>\n'
            f"{details_extra}\n"
            f'<pre><code>claude plugin install {html.escape(p["name"])}@polymath</code></pre>\n'
            f"{readme_html}"
        )
        page = PAGE_SHELL.format(
            title=f'{p["name"]} · Polymath',
            root="../",
            body=body,
        )
        plugin_html_path = SITE_DIR / "plugins" / f'{p["name"]}.html'
        if write_if_changed(plugin_html_path, page, check):
            diffs.append(plugin_html_path)

    if check and diffs:
        print(f"build-catalog: {len(diffs)} files would change:")
        for d in diffs:
            print(f"  {d.relative_to(REPO_ROOT)}")
        return 1

    if not check:
        print(f"build-catalog: wrote {len(diffs)} file(s) (no-op for unchanged files)")
    else:
        print("build-catalog: clean (no changes needed)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="exit non-zero if regenerating would change files")
    args = parser.parse_args(argv)
    return build(check=args.check)


if __name__ == "__main__":
    sys.exit(main())
