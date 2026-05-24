---
plugin: polymath-connector-notion
scenario: sync-prd
expect:
  invoked:
    - polymath-connector-notion:sync-doc-to-notion
  output_matches:
    - "(sync.key|sync-key)"
    - "(drift|last.synced|last_edited)"
    - "(source|backlink|repo)"
timeout_seconds: 90
---

# Prompt

> Sync docs/prds/refund-async-writes.md to Notion under the
> Engineering › PRDs parent page.

Use polymath-connector-notion:sync-doc-to-notion.

# Acceptance

- Sync-key derived from repo path; existing page updated rather than duplicated.
- Repo source URL pinned as a backlink on the page.
- Drift check performed before overwrite (warn if a human edited in Notion).
- Local sync marker saved under .polymath/notion-sync/.
