"""CLI for extracting key facilities near PSS/E flowgate elements.

Usage:
    python key_facilities.py --mon FLOWGATES.mon --raw MODEL.raw \\
        --areas 1 2 3 --out-dir OUT/

Writes branches.csv, generators.csv, transformers_3w.csv, unresolved.csv
to --out-dir.

The --areas argument is required: it restricts the search to those PSS/E
area IDs. Seeds whose buses fall outside the listed areas will appear in
unresolved.csv with reason 'bus_not_found'.
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from psse_model_util.model import Model
from psse_model_util.flowgate import (
    DEFAULT_GEN_MIN_MW,
    DEFAULT_HOPS,
    DEFAULT_KV_MAX,
    DEFAULT_KV_MIN,
    DEFAULT_SC,
    collect_key_facilities,
    filter_by_sc,
    parse_mon_file,
    resolve_elements,
)

logger = logging.getLogger("key_facilities")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mon", required=True, type=Path, help="Path to .mon flowgate file")
    p.add_argument("--raw", required=True, type=Path, help="Path to PSS/E .raw model")
    p.add_argument(
        "--areas",
        required=True,
        type=int,
        nargs="+",
        metavar="AREA_ID",
        help=(
            "Area IDs (integers) restricting the search domain. Required; "
            "no default. Example: --areas 1 2 3"
        ),
    )
    p.add_argument("--out-dir", required=True, type=Path, help="Output directory for CSVs")
    p.add_argument("--hops", type=int, default=DEFAULT_HOPS)
    p.add_argument("--kv-min", type=float, default=DEFAULT_KV_MIN)
    p.add_argument("--kv-max", type=float, default=DEFAULT_KV_MAX)
    p.add_argument("--gen-min-mw", type=float, default=DEFAULT_GEN_MIN_MW)
    p.add_argument("--sc", default=DEFAULT_SC, help="Security Coordinator filter")
    p.add_argument("-v", "--verbose", action="store_true")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )

    args.out_dir.mkdir(parents=True, exist_ok=True)

    fgs = parse_mon_file(args.mon)
    fgs_filtered = filter_by_sc(fgs, sc=args.sc)
    logger.info(
        "Parsed %d flowgates -> %d %s", len(fgs), len(fgs_filtered), args.sc
    )

    model = Model(args.raw)
    # Restrict the search domain to the requested areas before resolution.
    # Network.filter_by_area keeps any equipment with at least one bus in the
    # area set, mutates in place, and clears the cached graph.
    model.network.filter_by_area(args.areas, inplace=True)
    logger.info("Filtered model to areas %s", sorted(set(args.areas)))

    seeds, unresolved = resolve_elements(fgs_filtered, model)
    total_elements = sum(len(fg.monitor) + len(fg.contingency) for fg in fgs_filtered)
    logger.info(
        "Resolved %d/%d seeds (%d unresolved)",
        len(seeds), total_elements, len(unresolved),
    )

    out = {
        **collect_key_facilities(
            model,
            seeds,
            hops=args.hops,
            kv_min=args.kv_min,
            kv_max=args.kv_max,
            gen_min_mw=args.gen_min_mw,
        ),
        "unresolved": unresolved,
    }

    summary_parts = []
    for name, df in out.items():
        path = args.out_dir / f"{name}.csv"
        df.to_csv(path, index=False)
        summary_parts.append(f"{name}.csv ({len(df)} rows)")

    print(f"Wrote {', '.join(summary_parts)} to {args.out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
