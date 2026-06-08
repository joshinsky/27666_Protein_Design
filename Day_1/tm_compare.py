#!/usr/bin/env python3
"""Structural comparison with TM-align - batch (single-job) version.

Command-line equivalent of tm_compare_batch.ipynb. Compares one reference
structure against all .pdb structures in a target folder using tmtools
(a Python wrapper around TM-align). Each file is assumed to contain a single
chain; the first chain is read.

TM-score is NOT symmetric. Because the reference is always structure 1,
'TM (norm. by reference)' uses the same denominator for every target and is
the fair column for ranking targets against the reference.

Usage (defaults match the repo layout):
    python tm_compare.py
    python tm_compare.py --ref-dir data/input_vhh --target-dir data/target_vhh
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Non-interactive backend so plotting works on compute nodes (no display).
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from tmtools import tm_align  # noqa: E402
from tmtools.io import get_structure, get_residue_data  # noqa: E402


def find_structures(folder: Path) -> list[Path]:
    """Return sorted .pdb files in a folder."""
    return sorted(folder.glob("*.pdb"))


def load(path: Path):
    """Read the first chain of a file; return (coords, sequence)."""
    chain = next(get_structure(str(path)).get_chains())
    coords, seq = get_residue_data(chain)
    return np.ascontiguousarray(coords, dtype=np.float64), seq


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ref-dir", type=Path, default=Path("data/input_vhh"),
                   help="Folder holding the single reference structure")
    p.add_argument("--target-dir", type=Path, default=Path("data/target_vhh"),
                   help="Folder holding the structures to compare against")
    p.add_argument("--out-dir", type=Path, default=Path("results"),
                   help="Where to write the CSV and plot")
    p.add_argument("--ref-file", type=Path, default=None,
                   help="Explicit reference .pdb (overrides --ref-dir pick)")
    args = p.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)

    # --- Resolve reference -------------------------------------------------
    if args.ref_file is not None:
        REF = args.ref_file
        if not REF.is_file():
            sys.exit(f"Reference file not found: {REF}")
    else:
        ref_files = find_structures(args.ref_dir)
        if not ref_files:
            sys.exit(f"No .pdb files found in {args.ref_dir}")
        REF = ref_files[0]

    targets = find_structures(args.target_dir)
    if not targets:
        sys.exit(f"No .pdb files found in {args.target_dir}")

    print(f"Reference: {REF.name}", flush=True)
    print(f"Targets:   {len(targets)} structures", flush=True)

    # --- Run comparison loop ----------------------------------------------
    ref_coords, ref_seq = load(REF)

    rows = []
    for t in targets:
        try:
            t_coords, t_seq = load(t)
            res = tm_align(ref_coords, t_coords, ref_seq, t_seq)
            rows.append({
                "target": t.name,
                "target_len": len(t_seq),
                "TM (norm. by reference)": round(res.tm_norm_chain1, 4),
                "TM (norm. by target)": round(res.tm_norm_chain2, 4),
                "RMSD (A)": round(res.rmsd, 3),
            })
        except Exception as e:  # noqa: BLE001 - skip unreadable file, keep going
            print(f"  [skipped] {t.name}: {e}", flush=True)

    if not rows:
        sys.exit("No comparisons succeeded.")

    df = (pd.DataFrame(rows)
          .sort_values("TM (norm. by reference)", ascending=False)
          .reset_index(drop=True))
    print(df.to_string(index=False), flush=True)

    # --- Save results ------------------------------------------------------
    csv_path = args.out_dir / "tm_results.csv"
    df.to_csv(csv_path, index=False)
    print(f"Saved {csv_path}", flush=True)

    # --- Plot --------------------------------------------------------------
    plt.figure(figsize=(8, 4))
    plt.bar(df["target"], df["TM (norm. by reference)"])
    plt.axhline(0.5, linestyle="--", label="0.5 (same-fold threshold)")
    plt.ylabel("TM-score (normalized by reference)")
    plt.title(f"TM-score vs reference: {REF.name}")
    plt.xticks(rotation=45, ha="right")
    plt.legend()
    plt.tight_layout()
    plot_path = args.out_dir / "tm_scores.png"
    plt.savefig(plot_path, dpi=150)
    print(f"Saved {plot_path}", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
