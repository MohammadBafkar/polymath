#!/usr/bin/env python3
"""concurrency — Little's-law sizing for pools, workers, and queues.

  concurrency.py --rate 800 --latency-ms 45 --target-util 0.7
      in-flight work L = rate × latency; pool/workers needed = ceil(L ÷ util).

  concurrency.py --rate 800 --latency-ms 45 --target-util 0.7 \
      --cpu-ms 5 --cores 8
      adds thread-count guidance for a blocking-IO model:
      threads ≈ cores × util × (1 + wait ÷ cpu), where wait = latency − cpu.

  concurrency.py --rate 1200 --capacity 1000 --backlog 600000
      queue drain: backlog ÷ (capacity − rate); if capacity ≤ rate the
      backlog never drains.

Formulas (Little's law L = λ·W; Goetz thread-pool sizing). Inputs are rates in
req/s and times in ms. Exit 0 ok, 2 bad input.
"""

from __future__ import annotations

import argparse
import math
import sys


class InputError(Exception):
    pass


def fmt_duration(seconds: float) -> str:
    s = int(round(seconds))
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    parts = []
    if h:
        parts.append(f"{h}h")
    if m or h:
        parts.append(f"{m}m")
    parts.append(f"{sec}s")
    return " ".join(parts)


def run(a: argparse.Namespace) -> str:
    out: list[str] = ["Concurrency sizing (Little's law)"]
    if a.rate is None or a.rate <= 0:
        raise InputError("--rate must be > 0 (requests or jobs per second)")
    if not 0 < a.target_util <= 1:
        raise InputError("--target-util is a fraction in (0, 1], e.g. 0.7")

    have_sizing = a.latency_ms is not None
    if have_sizing:
        if a.latency_ms <= 0:
            raise InputError("--latency-ms must be > 0")
        in_flight = a.rate * a.latency_ms / 1000.0
        workers = math.ceil(in_flight / a.target_util)
        out.append(f"Arrival:   {a.rate:g}/s × {a.latency_ms:g} ms = {in_flight:.2f} in flight (L = λ·W)")
        out.append(
            f"Pool:      ceil({in_flight:.2f} ÷ {a.target_util:g}) = {workers} workers/connections "
            f"for utilization {a.target_util:g}"
        )
        if a.cpu_ms is not None or a.cores is not None:
            if a.cpu_ms is None or a.cores is None:
                raise InputError("--cpu-ms and --cores go together")
            if a.cpu_ms <= 0 or a.cores <= 0:
                raise InputError("--cpu-ms and --cores must be > 0")
            if a.cpu_ms > a.latency_ms:
                raise InputError("--cpu-ms cannot exceed --latency-ms")
            wait = a.latency_ms - a.cpu_ms
            threads = math.ceil(a.cores * a.target_util * (1 + wait / a.cpu_ms))
            cpu_util = a.rate * a.cpu_ms / 1000.0 / a.cores
            out.append(
                f"Threads:   ceil({a.cores:g} × {a.target_util:g} × (1 + {wait:g}/{a.cpu_ms:g})) = {threads} "
                f"(blocking-IO model; wait {wait:g} ms, cpu {a.cpu_ms:g} ms)"
            )
            verdict = "OK" if cpu_util <= a.target_util else "OVER target: add cores or cut CPU per request"
            out.append(f"CPU:       {a.rate:g}/s × {a.cpu_ms:g} ms ÷ {a.cores:g} cores = {cpu_util * 100:.0f}% — {verdict}")
    elif a.cpu_ms is not None or a.cores is not None:
        raise InputError("--cpu-ms/--cores need --latency-ms")

    if a.capacity is not None:
        if a.capacity <= 0:
            raise InputError("--capacity must be > 0")
        if a.backlog is None or a.backlog < 0:
            raise InputError("--capacity needs --backlog >= 0")
        if a.capacity <= a.rate:
            out.append(
                f"Queue:     capacity {a.capacity:g}/s ≤ arrival {a.rate:g}/s → backlog {a.backlog:g} never drains"
            )
        else:
            drain = a.backlog / (a.capacity - a.rate)
            out.append(
                f"Queue:     {a.backlog:g} ÷ ({a.capacity:g} − {a.rate:g}) = {fmt_duration(drain)} to drain"
            )
    elif a.backlog is not None:
        raise InputError("--backlog needs --capacity")

    if not have_sizing and a.capacity is None:
        raise InputError("give --latency-ms (sizing) and/or --capacity with --backlog (drain)")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--rate", type=float, help="arrival rate, per second")
    ap.add_argument("--latency-ms", type=float, help="mean time in system per request (service + wait), ms")
    ap.add_argument("--target-util", type=float, default=0.7, help="planned utilization (default 0.7)")
    ap.add_argument("--cpu-ms", type=float, help="CPU time per request, ms")
    ap.add_argument("--cores", type=float, help="cores available")
    ap.add_argument("--capacity", type=float, help="drain capacity, per second")
    ap.add_argument("--backlog", type=float, help="queued items")
    args = ap.parse_args()
    try:
        print(run(args))
    except InputError as e:
        print(f"concurrency: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
