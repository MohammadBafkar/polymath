#!/usr/bin/env python3
"""plan-summary — deterministic classification of a `terraform show -json` plan.

  terraform show -json tfplan.binary > tfplan.json
  plan-summary.py tfplan.json [--scope 'module.refunds.*' --scope 'aws_sqs_queue.refund_*']

Prints, in a fixed order: counts by action, destructive actions (with the
attributes that forced each replacement), stateful / IAM / network-exposure
callouts, out-of-scope changes, drift, providers without a version constraint,
and the MINIMUM gate the plan's shape allows. Values are never printed —
only addresses, actions, and attribute paths — so sensitive data in the plan
JSON cannot leak through this summary.

Minimum gate (the reviewer may raise it, never lower it):
  block               a delete/replace outside the approved --scope
  apply-with-approval any delete/replace, IAM change, or 0.0.0.0/0 ingress
  apply-ok            otherwise

Exit 0 ok, 2 unreadable or non-plan JSON.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys

STATEFUL = re.compile(
    r"^(aws_db_instance|aws_rds_cluster|aws_dynamodb_table|aws_elasticache_|aws_efs_file_system|aws_ebs_volume"
    r"|aws_s3_bucket$|google_sql_database_instance|google_storage_bucket$|google_bigtable_|google_spanner_"
    r"|azurerm_mssql_database|azurerm_postgresql_|azurerm_cosmosdb_|azurerm_storage_account$|azurerm_managed_disk)"
)
IAM = re.compile(r"^(aws_iam_|google_project_iam_|google_service_account|azurerm_role_assignment|azurerm_role_definition)")
NETWORK = re.compile(r"(security_group|firewall|network_security_rule)")
OPEN_CIDRS = ("0.0.0.0/0", "::/0")


class InputError(Exception):
    pass


def classify(actions: list[str]) -> str:
    a = list(actions or [])
    if a in (["delete", "create"], ["create", "delete"]):
        return "replace"
    if a == ["create"]:
        return "create"
    if a == ["update"]:
        return "update"
    if a == ["delete"]:
        return "delete"
    if a == ["read"]:
        return "read"
    if a == ["forget"]:
        return "forget"
    return "no-op"


def opens_world(after) -> bool:
    """True if any value under `after` is an open CIDR (checked by value, never printed)."""
    if isinstance(after, dict):
        return any(opens_world(v) for v in after.values())
    if isinstance(after, list):
        return any(opens_world(v) for v in after)
    return isinstance(after, str) and after in OPEN_CIDRS


def path_str(path) -> str:
    return ".".join(str(p) for p in path) if isinstance(path, list) else str(path)


def summarize(plan: dict, scope: list[str]) -> str:
    if "resource_changes" not in plan and "format_version" not in plan:
        raise InputError("not a plan JSON — produce it with `terraform show -json <planfile>`")
    counts = {k: 0 for k in ("create", "update", "replace", "delete", "forget", "read")}
    destructive, stateful, iam, exposed, out_of_scope = [], [], [], [], []
    for rc in sorted(plan.get("resource_changes", []), key=lambda r: r.get("address", "")):
        addr, rtype = rc.get("address", "?"), rc.get("type", "")
        change = rc.get("change", {})
        kind = classify(change.get("actions"))
        if kind == "no-op":
            continue
        counts[kind] += 1
        if kind in ("replace", "delete"):
            why = ""
            if kind == "replace":
                paths = [path_str(p) for p in change.get("replace_paths") or []]
                reason = rc.get("action_reason", "")
                why = f"  forced by: {', '.join(paths) or '?'}" + (f" ({reason})" if reason else "")
            destructive.append(f"  - {addr:<48} {kind.upper()}{why}")
            if STATEFUL.match(rtype):
                stateful.append(f"  - {addr} ({rtype}) {kind.upper()} — data-loss gate: snapshot/backup + restore path required")
        if IAM.match(rtype) and kind != "read":
            iam.append(f"  - {addr} {kind}")
        if NETWORK.search(rtype) and kind in ("create", "update", "replace") and opens_world(change.get("after")):
            exposed.append(f"  - {addr} {kind} — ingress open to the internet (0.0.0.0/0 or ::/0)")
        if scope and kind in ("create", "replace", "delete", "update") and not any(fnmatch.fnmatch(addr, g) for g in scope):
            out_of_scope.append(f"  - {addr} {kind}")

    drift = [f"  - {d.get('address', '?')} {classify(d.get('change', {}).get('actions'))}"
             for d in sorted(plan.get("resource_drift", []), key=lambda r: r.get("address", ""))]
    unpinned = sorted(
        name for name, cfg in (plan.get("configuration", {}).get("provider_config", {}) or {}).items()
        if not cfg.get("version_constraint")
    )

    oos_destructive = [l for l in out_of_scope if l.rstrip().endswith(("replace", "delete"))]
    if oos_destructive:
        gate = "block (destructive change outside the approved scope)"
    elif destructive or iam or exposed:
        gate = "apply-with-approval (destructive, IAM, or internet-exposure change present)"
    else:
        gate = "apply-ok (no destructive, IAM, or exposure change)"

    tf_add = counts["create"] + counts["replace"]
    tf_destroy = counts["delete"] + counts["replace"]
    out = [
        "Plan summary",
        f"  create {counts['create']} · update {counts['update']} · replace {counts['replace']} · "
        f"delete {counts['delete']} · forget {counts['forget']} · deferred read {counts['read']}",
        f"  (terraform's own line: {tf_add} to add, {counts['update']} to change, {tf_destroy} to destroy)",
        "",
        "Destructive actions:",
        *(destructive or ["  none"]),
        "",
        "Stateful resources at risk:",
        *(stateful or ["  none"]),
        "",
        "IAM / privilege changes (own reviewer):",
        *(iam or ["  none"]),
        "",
        "Internet exposure:",
        *(exposed or ["  none"]),
        "",
        "Outside approved scope:" if scope else "Outside approved scope: (no --scope given — not checked)",
        *((out_of_scope or ["  none"]) if scope else []),
        "",
        "Drift (changed outside Terraform — not this PR's intent):",
        *(drift or ["  none"]),
        "",
        "Providers without a version constraint: " + (", ".join(unpinned) if unpinned else "none"),
        "",
        f"Minimum gate: {gate}",
    ]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Classify a terraform plan JSON deterministically.")
    ap.add_argument("plan", help="tfplan.json from `terraform show -json`")
    ap.add_argument("--scope", action="append", default=[], help="address glob the PR is approved to change (repeatable)")
    args = ap.parse_args(argv)
    try:
        try:
            with open(args.plan) as fh:
                plan = json.load(fh)
        except (OSError, json.JSONDecodeError) as e:
            raise InputError(f"cannot read {args.plan}: {e}")
        if not isinstance(plan, dict):
            raise InputError("plan JSON must be an object")
        print(summarize(plan, args.scope))
    except InputError as e:
        print(f"plan-summary: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
