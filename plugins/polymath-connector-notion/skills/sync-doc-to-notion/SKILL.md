---
name: sync-doc-to-notion
description: Mirror a local Markdown artifact (PRD, postmortem, ADR) to a Notion page — preserves headings + lists + code blocks, links back to the repo source.
---

# sync-doc-to-notion

> Push a Markdown artifact into Notion as a page with a stable identifier so subsequent edits update the same page rather than spawning duplicates. Output is the Notion page URL + the local sync marker.

## When to use

- A PRD, postmortem, or ADR is canonical in the repo but stakeholders read in Notion.
- A `respondToIncident` step asks for an incident report visible to non-eng teams.
- A `releaseTrain` step needs the release notes mirrored to the company changelog page.

## Inputs

- Source Markdown file (required) — repo path; this is the source of truth.
- Target parent page ID (optional) — defaults to `userConfig.notionRootPageId`.
- Artifact slug (required) — kebab-case identifier; pairs with the repo path to form the sync key.

## Procedure

1. **Compute the sync key.** `sha256(repo-relative-path)[:12]` — stable across renames if the slug is preserved separately. Store under `notion.syncKey` as a page property; query by it before creating to avoid duplicates.
2. **Resolve target page.** Search the parent page for a child whose `notion.syncKey` matches. If found, update it; otherwise create a new child.
3. **Convert Markdown → Notion blocks.**
   - Headings 1-3 → `heading_1`/`heading_2`/`heading_3`.
   - Paragraphs → `paragraph` with inline rich-text runs preserving bold/italic/code.
   - Bulleted / numbered lists → matching Notion list blocks; nest correctly.
   - Code blocks → `code` with the language hint.
   - Tables → `table` block (Notion's row-based shape; flatten complex Markdown tables).
   - Images → upload via the notion MCP's image-upload tool and embed; never link directly to a localhost URL.
4. **Write a backlink.** First block of the page is a callout: `Source: <repo URL>/blob/<branch>/<path>`. Pins the source of truth.
5. **Preserve metadata.** Page properties: `sync-key` (string), `last-synced` (date), `commit-sha` (string).
6. **Save a local sync marker** at `.polymath/notion-sync/<slug>.json` with `{ pageId, lastSynced, commitSha }`. Allows future runs to detect drift (page edited in Notion after last sync).
7. **Detect drift before overwriting.** If the Notion page's `last_edited_time` is newer than the marker's `lastSynced` AND the Notion editor is not the integration, warn the user before overwriting — someone hand-edited in Notion.

## Output

```text
sync-doc-to-notion: docs/prds/refund-async-writes.md

Target:        Workspace › Engineering › PRDs (parent: notion-page-id)
Sync key:      sha256(docs/prds/refund-async-writes.md)[:12] → 7d9a3f1b2cde
Action:        updated (existing page found by sync-key)
Page URL:      https://www.notion.so/Refund-Async-Writes-1a2b...
Drift check:   clean (last Notion edit by integration on 2026-05-10)

Saved marker: .polymath/notion-sync/refund-async-writes.json
```

## Quality bar

- Repo path is the source of truth (page is a mirror, not the canonical doc).
- Sync key prevents duplicate pages on re-runs.
- Backlink to the repo source pinned as the first block.
- Drift detected before overwriting — flag, do not silently overwrite.

## Anti-patterns to avoid

- Creating a new page on every sync. Spams Notion search and confuses readers.
- Two-way sync without conflict handling. Notion's rich-text model is lossier than Markdown; round-tripping degrades content.
- Embedding images by localhost URL. Notion fetches them at render time; they will 404 from anywhere but your machine.
- Sharing the integration with the workspace root. Scope to specific parent pages.
