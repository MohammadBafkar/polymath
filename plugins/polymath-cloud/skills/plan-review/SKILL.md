---
name: plan-review
description: Read a terraform plan (binary or JSON) and surface destructive actions, drift, and unsafe diffs before apply.
---

# plan-review

> A second pair of eyes on a `terraform plan` output. Output is a categorized review: destructive actions, drift, replacements, additions, and a go/no-go recommendation.

**Mode:** deterministic — same inputs, same output. Follow the steps and the output shape exactly; compute with the named script or tool, never by estimate; add nothing the shape does not ask for.

## When to use

- A PR includes a generated plan artifact (`tfplan.binary` or `tfplan.json`) and a reviewer wants a fast read.
- Pre-apply, before promoting a plan to prod.
- After a long-lived branch rebases, to catch drift that crept in.

## Inputs

- Plan file (required) — either `tfplan.binary` (run `terraform show -json tfplan.binary > tfplan.json` first) or `tfplan.json` directly.
- Workspace / environment label (required) — review tone is stricter for `prod`.
- Approved change scope (optional) — what the PR claims to change. Anything outside is flagged.

## Procedure

1. **Convert if needed.** If a binary plan is supplied, run `terraform show -json <plan>` (or `tofu show -json`, or the binary named in the plugin's `terraformBinary` setting) to produce JSON. Do not parse the binary format directly. **The JSON contains sensitive values in plaintext** (`before_sensitive`/`after_sensitive` only *mark* them): never echo those values in your review, and flag a `tfplan.json` uploaded as a public CI artifact or committed to the repo.
2. **Run the bundled summary — never classify a plan by reading the JSON by eye.** It applies the rules in steps 3–6 mechanically, never prints a value, and states the minimum gate:

   ```bash
   python3 "${POLYMATH_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}/skills/plan-review/scripts/plan-summary.py" tfplan.json \
     --scope 'module.refunds.*'      # one --scope per address glob the PR is approved to change
   ```

   Paste its block verbatim, then add only what it cannot know (steps 3–6 explain each section). Exit 2 = not a plan JSON.
3. **Read each classification** (the script's `change.actions` mapping):
   - `["no-op"]` — unchanged; ignore. `["read"]` — data source read; note only if it's deferred to apply time.
   - `["forget"]` — removed from state without destroying (a `removed` block); confirm that's intended.
   - `["create"]` — new resources; flag if outside approved scope.
   - `["update"]` — in-place change; show before → after for sensitive fields.
   - `["delete", "create"]` or `["create", "delete"]` — replacement; almost always destructive (state loss). Read `action_reason` and `replace_paths` to see *which attribute* forced it — often a one-line config fix avoids the replace.
   - `["delete"]` — destruction; only safe with explicit approval.
4. **Destructive patterns** the script calls out by resource type — add the human gate for each:
   - `aws_db_instance`, `aws_rds_cluster`, `google_sql_database_instance`, `azurerm_mssql_database` — replacement triggers backup-required gate.
   - `aws_s3_bucket`, `google_storage_bucket`, `azurerm_storage_account` — delete triggers data-loss gate (require `force_destroy = false` audit).
   - `aws_iam_*`, `google_project_iam_*`, `azurerm_role_assignment` — privilege changes deserve their own reviewer; wildcard actions/resources (`"*"`) and new cross-account trust get a dedicated callout.
   - `*_security_group`, `*_firewall*` — surface opening (0.0.0.0/0 ingress) gets a dedicated callout.
5. **Drift.** Read the plan JSON's top-level `resource_drift` array — changes Terraform detected during refresh that happened outside Terraform. Report them separately from intended changes; an update in `resource_changes` that merely reverts drift is not part of the PR's intent either.
6. **Sensitive-field check** (judgment — the script can't see CI logs). Confirm sensitive attributes are marked (`after_sensitive`) and that the CI log shows `(sensitive value)` rather than the value; flag any secret that appears unmasked in plan *output* or in a non-sensitive attribute (e.g. a password in a tag or user_data).
7. **Provider version pinning.** The script lists providers without a version constraint — they float and re-plan unpredictably.
8. **Recommend** one of `apply-ok`, `apply-with-approval`, `needs-rework`, `block`. Start from the script's minimum gate; raise it only for a named reason (an out-of-scope create/update, a replacement a one-line config change avoids, an unmasked secret, a missing backup for a stateful replace). Never lower it.

## Output

```text
plan-review

Workspace:   prod
Plan file:   tfplan.json

Plan summary
  create 4 · update 2 · replace 1 · delete 1 · forget 0 · deferred read 0
  (terraform's own line: 5 to add, 2 to change, 2 to destroy)

Destructive actions:
  - aws_db_instance.refund_primary                   REPLACE  forced by: engine_version (replace_because_cannot_update)
  - aws_s3_bucket.legacy_uploads                     DELETE

Stateful resources at risk:
  - aws_db_instance.refund_primary (aws_db_instance) REPLACE — data-loss gate: snapshot/backup + restore path required
  - aws_s3_bucket.legacy_uploads (aws_s3_bucket) DELETE — data-loss gate: snapshot/backup + restore path required

IAM / privilege changes (own reviewer):
  none

Internet exposure:
  none

Outside approved scope:
  - aws_s3_bucket.legacy_uploads delete

Drift (changed outside Terraform — not this PR's intent):
  - aws_security_group.web update

Providers without a version constraint: none

Minimum gate: block (destructive change outside the approved scope)

Reviewer notes
  - refund_primary: engine upgrade 14 → 15 forces replacement; use an in-place major-version
    upgrade (allow_major_version_upgrade) instead, or confirm skip_final_snapshot = false + restore runbook.
  - Sensitive values: masked in the CI plan output; tfplan.json is not uploaded as an artifact.

Recommendation: block
  Reason: legacy_uploads delete is outside PR scope — split it into a dedicated migration PR.
```

## Quality bar

- Every destructive action explicitly named (resource type + address + risk + gate).
- Drift separated from intentional change.
- Sensitive field handling verified.
- A single explicit recommendation, not "looks fine".

## Anti-patterns to avoid

- Approving a plan by file size or count ("only 6 changes, should be fine"). Volume is not risk.
- Treating a replacement as an update. Replacement = delete + create, with state loss.
- Skipping the drift section because it "doesn't change anything in this PR". Drift is the leading indicator of out-of-band changes that bypass review.
- Reviewing a binary plan by reading it directly. Always go through `terraform show -json` first.
- Quoting a sensitive value from the plan JSON in the review.
