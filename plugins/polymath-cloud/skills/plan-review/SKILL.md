---
name: plan-review
description: Read a terraform plan (binary or JSON) and surface destructive actions, drift, and unsafe diffs before apply.
---

# plan-review

> A second pair of eyes on a `terraform plan` output. Output is a categorized review: destructive actions, drift, replacements, additions, and a go/no-go recommendation.

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
2. **Classify every resource change** by `change.actions`:
   - `["no-op"]` — unchanged; ignore. `["read"]` — data source read; note only if it's deferred to apply time.
   - `["forget"]` — removed from state without destroying (a `removed` block); confirm that's intended.
   - `["create"]` — new resources; flag if outside approved scope.
   - `["update"]` — in-place change; show before → after for sensitive fields.
   - `["delete", "create"]` or `["create", "delete"]` — replacement; almost always destructive (state loss). Read `action_reason` and `replace_paths` to see *which attribute* forced it — often a one-line config fix avoids the replace.
   - `["delete"]` — destruction; only safe with explicit approval.
3. **Flag destructive patterns** by resource type:
   - `aws_db_instance`, `aws_rds_cluster`, `google_sql_database_instance`, `azurerm_mssql_database` — replacement triggers backup-required gate.
   - `aws_s3_bucket`, `google_storage_bucket`, `azurerm_storage_account` — delete triggers data-loss gate (require `force_destroy = false` audit).
   - `aws_iam_*`, `google_project_iam_*`, `azurerm_role_assignment` — privilege changes deserve their own reviewer; wildcard actions/resources (`"*"`) and new cross-account trust get a dedicated callout.
   - `*_security_group`, `*_firewall*` — surface opening (0.0.0.0/0 ingress) gets a dedicated callout.
4. **Detect drift.** Read the plan JSON's top-level `resource_drift` array — changes Terraform detected during refresh that happened outside Terraform. Report them separately from intended changes; an update in `resource_changes` that merely reverts drift is not part of the PR's intent either.
5. **Sensitive-field check.** Confirm sensitive attributes are marked (`after_sensitive`) and that the CI log shows `(sensitive value)` rather than the value; flag any secret that appears unmasked in plan *output* or in a non-sensitive attribute (e.g. a password in a tag or user_data).
6. **Provider version pinning.** Note any providers without a version constraint — they will float and re-plan unpredictably.
7. **Recommend** one of: `apply-ok`, `apply-with-approval`, `needs-rework`, `block`.

## Output

```text
plan-review

Workspace:   prod
Plan file:   tfplan.json

Summary
  add:      4
  change:   2
  destroy:  1
  replace:  1

Destructive actions (require explicit approval):
  - aws_db_instance.refund_primary    REPLACE  (engine_version 14.10 → 15.4)
    Risk: replacement drops local data unless final snapshot is taken.
    Gate: confirm `skip_final_snapshot = false` + restore procedure documented.

  - aws_s3_bucket.legacy_uploads      DESTROY
    Risk: bucket holds 4.2 TB of historical uploads.
    Gate: out-of-scope for this PR; remove from plan or split into a dedicated migration PR.

Drift (configuration matches prior state; cloud changed underneath):
  - aws_security_group.web tag.cost-center: "platform" → "platform-2025"

Recommendation: needs-rework
  Reason: legacy_uploads destroy was not in PR scope.
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
