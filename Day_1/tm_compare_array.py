#!/usr/bin/env python3
"""TM-align array worker - compares the reference against ONE target.

Used by the job-array route: each LSF array task runs this once with
--index $LSB_JOBINDEX and writes a single-row CSV into results/parts/.
merge_results.py then combines the parts into the final table + plot.

Usage:
    python tm_compare_array.py --index 1
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from tmtools import tm_align
from tmtools.io import get_structure, get_residue_data


def find_structures(folder: Path) -> list[Path]:
    return sorted(folder.glob("*.pdb"))


def load(path: Path):
    chain = next(get_structure(str(path)).get_chains())
    coords, seq = get_residue_data(chain)
    return np.ascontiguousarray(coords, dtype=np.float64), seq


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ref-dir", type=Path, default=Path("data/input_vhh"))
    p.add_argument("--target-dir", type=Path, default=Path("data/target_vhh"))
    p.add_argument("--out-dir", type=Path, default=Path("results/parts"))
    p.add_argument("--index", type=int, required=True,
                   help="1-based target index (LSB_JOBINDEX)")
    args = p.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)

    ref_files = find_structures(args.ref_dir)
    if not ref_files:
        sys.exit(f"No .pdb files found in {args.ref_dir}")
    REF = ref_files[0]

    targets = find_structures(args.target_dir)
    if not (1 <= args.index <= len(targets)):
        sys.exit(f"Index {args.index} out of range 1..{len(targets)}")
    t = targets[args.index - 1]

    ref_coords, ref_seq = load(REF)
    try:
        t_coords, t_seq = load(t)
        res = tm_align(ref_coords, t_coords, ref_seq, t_seq)
        row = {
            "target": t.name,
            "target_len": len(t_seq),
            "TM (norm. by reference)": round(res.tm_norm_chain1, 4),
            "TM (norm. by target)": round(res.tm_norm_chain2, 4),
            "RMSD (A)": round(res.rmsd, 3),
        }
    except Exception as e:  # noqa: BLE001
        print(f"[skipped] {t.name}: {e}", flush=True)
        return 0

    out = args.out_dir / f"part_{args.index:04d}.csv"
    pd.DataFrame([row]).to_csv(out, index=False)
    print(f"Saved {out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
