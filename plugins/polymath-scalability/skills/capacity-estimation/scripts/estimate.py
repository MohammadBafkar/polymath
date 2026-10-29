#!/usr/bin/env python3
"""estimate — back-of-envelope capacity arithmetic for a system design.

  estimate.py --dau 5000000 --actions-per-user-day 20 --read-ratio 0.9 \
      --peak-factor 3 --read-bytes 5000 --write-bytes 2000 \
      --retention-days 365 --replication 3 --cache-hit 0.8 \
      --per-node-qps 2000 --target-util 0.6

Inputs are the caller's assumptions; every figure below is derived from them
and nothing else.

  total/day  = dau × actions-per-user-day
  avg QPS    = total/day ÷ 86,400
  peak QPS   = avg QPS × peak-factor
  read QPS   = peak QPS × read-ratio;  write QPS = peak QPS − read QPS
  ingress    = write QPS × write-bytes;  egress = read QPS × read-bytes
  storage    = total/day × (1 − read-ratio) × write-bytes × retention-days × replication
  origin QPS = read QPS × (1 − cache-hit)  (+ write QPS) — what the data tier must serve
  nodes      = ceil(peak QPS ÷ (per-node-qps × target-util)) + 1  (N+1)   [when --per-node-qps is given]

Units are decimal SI (1 KB = 1,000 B; 1 TB = 10^12 B), network in MB/s and
Mbit/s. Exit 0 ok, 2 bad input.
"""

from __future__ import annotations

import argparse
import math
import sys

SECONDS_PER_DAY = 86_400


class InputError(Exception):
    pass


def human_bytes(n: float) -> str:
    for unit, size in (("PB", 1e15), ("TB", 1e12), ("GB", 1e9), ("MB", 1e6), ("KB", 1e3)):
        if n >= size:
            return f"{n / size:.2f} {unit}"
    return f"{n:.0f} B"


def human_count(n: float) -> str:
    for unit, size in (("B", 1e9), ("M", 1e6), ("K", 1e3)):
        if n >= size:
            return f"{n / size:.2f}{unit}"
    return f"{n:.0f}"


def positive(name: str, value: float) -> float:
    if value <= 0:
        raise InputError(f"{name} must be > 0")
    return value


def compute(a: argparse.Namespace) -> dict:
    positive("--dau", a.dau)
    positive("--actions-per-user-day", a.actions_per_user_day)
    positive("--peak-factor", a.peak_factor)
    positive("--retention-days", a.retention_days)
    positive("--replication", a.replication)
    if not 0 <= a.read_ratio <= 1:
        raise InputError("--read-ratio is a fraction in [0, 1], e.g. 0.9")
    if not 0 <= a.cache_hit < 1:
        raise InputError("--cache-hit is a fraction in [0, 1), e.g. 0.8")
    if a.read_bytes < 0 or a.write_bytes < 0:
        raise InputError("--read-bytes and --write-bytes must be >= 0")
    if a.per_node_qps is not None:
        positive("--per-node-qps", a.per_node_qps)
        if not 0 < a.target_util <= 1:
            raise InputError("--target-util is a fraction in (0, 1], e.g. 0.6")

    total_day = a.dau * a.actions_per_user_day
    avg_qps = total_day / SECONDS_PER_DAY
    peak_qps = avg_qps * a.peak_factor
    read_qps = peak_qps * a.read_ratio
    write_qps = peak_qps - read_qps
    ingress = write_qps * a.write_bytes
    egress = read_qps * a.read_bytes
    writes_day = total_day * (1 - a.read_ratio)
    stored = writes_day * a.write_bytes * a.retention_days * a.replication
    origin_qps = read_qps * (1 - a.cache_hit) + write_qps
    nodes = None
    if a.per_node_qps is not None:
        nodes = math.ceil(peak_qps / (a.per_node_qps * a.target_util)) + 1
    return dict(total_day=total_day, avg_qps=avg_qps, peak_qps=peak_qps, read_qps=read_qps,
                write_qps=write_qps, ingress=ingress, egress=egress, writes_day=writes_day,
                stored=stored, origin_qps=origin_qps, nodes=nodes)


def render(a: argparse.Namespace, r: dict) -> str:
    out = [
        "Capacity estimate (assumptions are inputs, not facts)",
        f"Inputs:    dau {human_count(a.dau)} · {a.actions_per_user_day:g} actions/user/day · "
        f"read ratio {a.read_ratio:g} · peak ×{a.peak_factor:g}",
        f"           read {human_bytes(a.read_bytes)}/req · write {human_bytes(a.write_bytes)}/req · "
        f"retain {a.retention_days:g} d · replication ×{a.replication:g} · cache hit {a.cache_hit:g}",
        "",
        f"Requests:  {human_count(r['total_day'])}/day → avg {r['avg_qps']:,.0f} QPS → peak {r['peak_qps']:,.0f} QPS",
        f"           reads {r['read_qps']:,.0f}/s · writes {r['write_qps']:,.0f}/s",
        f"Origin:    {r['origin_qps']:,.0f} QPS reach the data tier "
        f"({r['read_qps'] * (1 - a.cache_hit):,.0f} read misses + {r['write_qps']:,.0f} writes)",
        f"Network:   ingress {r['ingress'] / 1e6:,.2f} MB/s ({r['ingress'] * 8 / 1e6:,.1f} Mbit/s) · "
        f"egress {r['egress'] / 1e6:,.2f} MB/s ({r['egress'] * 8 / 1e6:,.1f} Mbit/s)",
        f"Storage:   {human_count(r['writes_day'])} writes/day → "
        f"{human_bytes(r['stored'])} over {a.retention_days:g} d at ×{a.replication:g} replication",
    ]
    if r["nodes"] is not None:
        out.append(
            f"Nodes:     ceil({r['peak_qps']:,.0f} ÷ ({a.per_node_qps:g} × {a.target_util:g})) + 1 (N+1) = {r['nodes']}"
        )
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dau", type=float, required=True, help="daily active users")
    ap.add_argument("--actions-per-user-day", type=float, required=True)
    ap.add_argument("--read-ratio", type=float, required=True, help="fraction of requests that are reads")
    ap.add_argument("--peak-factor", type=float, default=3.0, help="peak QPS ÷ average QPS (default 3)")
    ap.add_argument("--read-bytes", type=float, default=0.0, help="bytes returned per read")
    ap.add_argument("--write-bytes", type=float, default=0.0, help="bytes stored per write")
    ap.add_argument("--retention-days", type=float, default=365.0)
    ap.add_argument("--replication", type=float, default=3.0, help="copies stored (default 3)")
    ap.add_argument("--cache-hit", type=float, default=0.0, help="read cache hit ratio (default 0)")
    ap.add_argument("--per-node-qps", type=float, default=None, help="measured QPS one node sustains")
    ap.add_argument("--target-util", type=float, default=0.6, help="planned node utilization (default 0.6)")
    args = ap.parse_args()
    try:
        print(render(args, compute(args)))
    except InputError as e:
        print(f"estimate: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
