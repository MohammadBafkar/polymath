---
artifact: PRDescription
schemaVersion: 0.1
title: "{{title}}"
type: "{{conventional_commit_type}}"
scope: "{{scope}}"
linked_prd: "{{prd_link}}"
---

## Summary

One paragraph in the active voice. What does this PR do? Why now?

## Motivation

Link to the PRD, ADR, or issue that motivated this change. If this is a fix,
quote the bug or failure mode.

- PRD: `{{prd_link}}`
- Related: `{{related_links}}`

## Changes

What this PR changes, grouped logically. Avoid pasting a file-by-file diff — the
reviewer can read the diff. Call out:

- New behavior or APIs
- Removed behavior or APIs
- Migration steps reviewers must take

## Test plan

- [ ] Unit tests cover {{behavior}}
- [ ] Integration / end-to-end test exercises {{scenario}}
- [ ] Manual verification: {{verification steps}}

## Risk and rollback

- Risk: …
- Rollback plan: …
- Feature flag: `{{flag}}` (if any)

## Reviewers

Tag specific people for parts of the change rather than the whole PR.

- {{area}}: @{{reviewer}}

## Checklist

- [ ] PR title follows Conventional Commits (`type(scope): summary`).
- [ ] CHANGELOG updated under `[Unreleased]`.
- [ ] Tests added or updated.
- [ ] Docs / runbooks updated if behavior or operations change.
- [ ] No secrets in diff (verified by `polymath-engineering` secret-scan hook).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
