#!/usr/bin/env python3
"""Extract CIF files from .cif.gz and compute per-atom nearest-chain distances.

Usage example:
  python cif_distance_analysis.py \
    --input-dir /work3/s212001/projects/binder_design/gzmK/exp_02_test_antihotspot/diffusion_out \
    --extracted-dir /work3/s212001/projects/binder_design/gzmK/exp_02_test_antihotspot/cif_files \
    --out-dir /work3/s212001/projects/binder_design/gzmK/exp_02_test_antihotspot/results \
    --atom "B:67:NE2" --atom "B:70:OG2" \
    --min-distance 0.0

The script will:
  1) Decompress any *.cif.gz in `--input-dir` into `--extracted-dir` (only once).
  2) For each decompressed .cif, compute the distance from each specified atom to the nearest
     atom in a different chain.
  3) Store per-atom distances + nearest-atom identity in a master CSV.
  4) Partition the master CSV into category-specific CSVs based on the 4 characters after
     the first "cfg" in the CIF filename.
  5) Generate a summary CSV with mean/median distances per (cfg category, atom spec).

Requirements:
  - biopython (Bio.PDB)
  - numpy

"""

from __future__ import annotations

import argparse
import csv
import gzip
import os
import re
import sys
from pathlib import Path

import numpy as np
try:
    import matplotlib.pyplot as plt
    _HAS_MATPLOTLIB = True
except ImportError:
    _HAS_MATPLOTLIB = False
from Bio.PDB import MMCIFParser


def decompress_cif_gz(input_dir: Path, out_dir: Path) -> list[tuple[Path, str]]:
    """Decompress all *.cif.gz (recursively) in input_dir into out_dir and return list of (cif_path, cfg_category)."""

    out_dir.mkdir(parents=True, exist_ok=True)
    decompressed = []

    for gz_path in sorted(input_dir.rglob("*.cif.gz")):
        rel_path = gz_path.relative_to(input_dir)
        parts = rel_path.parts
        cfg_cat = parts[0] if len(parts) >= 2 else "ROOT"

        out_path = out_dir / rel_path.with_suffix("")  # remove .gz while preserving subdirectory structure
        out_path.parent.mkdir(parents=True, exist_ok=True)

        if out_path.exists():
            decompressed.append((out_path, cfg_cat))
            continue

        with gzip.open(gz_path, "rt") as fin, open(out_path, "w") as fout:
            fout.write(fin.read())
        decompressed.append((out_path, cfg_cat))

    return decompressed


def extract_cfg_category(cif_path: Path) -> str:
    """Deprecated: cfg category is now derived from the input subfolder name."""
    return "UNKNOWN"


def parse_atom_spec(spec: str) -> tuple[str, str, str]:
    """Parse an atom spec of the form CHAIN:RESNUM:ATOMNAME."""

    parts = spec.split(":")
    if len(parts) != 3:
        raise ValueError(f"Invalid atom spec '{spec}'. Expected format CHAIN:RESNUM:ATOMNAME")
    chain_id, resnum, atom_name = parts
    return chain_id, resnum, atom_name


def find_atom(structure, chain_id: str, resnum: str, atom_name: str):
    """Return (Atom, chain_id) matching the spec, or (None, None) if not found.

    If chain_id begins with '~', treat it as a wildcard and search all chains for
    the first matching residue/atom.
    """

    model = next(structure.get_models())

    wildcard = chain_id.startswith("~")
    target_chain = chain_id[1:] if wildcard else chain_id

    # If wildcard, search all chains; otherwise just the requested chain.
    chains = list(model) if wildcard else ([model[target_chain]] if target_chain in model else [])

    for chain in chains:
        for res in chain:
            # res.get_id() returns (hetfield, resseq, icode)
            if str(res.get_id()[1]) == resnum:
                try:
                    atom = res[atom_name]
                except KeyError:
                    return None, None
                return atom, chain.id

    return None, None


def get_all_other_chain_atoms(structure, exclude_chain: str):
    """Return a list of atoms from all chains except exclude_chain."""

    model = next(structure.get_models())
    atoms = []
    for chain in model:
        if chain.id == exclude_chain:
            continue
        atoms.extend(list(chain.get_atoms()))
    return atoms


def compute_nearest(atom, other_atoms) -> tuple[float, str, str, str]:
    """Compute distance from atom to the nearest atom in other_atoms.

    Returns (distance, chain_id, resnum, atom_name).
    """

    if atom is None or not other_atoms:
        return float("nan"), "", "", ""

    src_coord = atom.get_coord()
    best = float("inf")
    best_hit = None
    for o in other_atoms:
        d = np.linalg.norm(src_coord - o.get_coord())
        if d < best:
            best = d
            best_hit = o
    if best_hit is None:
        return float("nan"), "", "", ""

    res = best_hit.get_parent()
    chain = res.get_parent()
    return best, chain.id, str(res.get_id()[1]), best_hit.get_name()


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def plot_summary(summary_rows: list[dict], out_dir: Path):
    """Plot mean+median distance per atom_spec across cfg categories."""

    # Group summary data by atom_spec
    by_atom = {}
    for r in summary_rows:
        atom = r["atom_spec"]
        by_atom.setdefault(atom, []).append(r)

    # Sort cfg categories alphanumerically (should work for your cfg formats)
    def cfg_key(cat: str):
        return cat

    n_atoms = len(by_atom)
    n_cols = min(3, n_atoms)
    n_rows = (n_atoms + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(4 * n_cols, 3 * n_rows), squeeze=False)
    axes = axes.flatten()

    for ax, (atom, rows) in zip(axes, sorted(by_atom.items())):
        rows_sorted = sorted(rows, key=lambda r: cfg_key(r["cfg_category"]))
        cfgs = [r["cfg_category"] for r in rows_sorted]
        means = [r["mean_distance"] for r in rows_sorted]
        meds = [r["median_distance"] for r in rows_sorted]

        x = range(len(cfgs))
        ax.plot(x, means, marker="o", label="mean")
        ax.plot(x, meds, marker="s", label="median")
        ax.set_xticks(x)
        ax.set_xticklabels(cfgs, rotation=45, ha="right")
        ax.set_title(atom)
        ax.set_ylabel("distance")
        ax.legend(fontsize=8)
        ax.grid(True, linestyle=":", alpha=0.5)

    # Turn off unused axes
    for ax in axes[len(by_atom) :]:
        ax.axis("off")

    fig.tight_layout()
    out_png = out_dir / "summary_by_cfg_and_atom.png"
    fig.savefig(out_png, dpi=200)
    plt.close(fig)
    print(f"Wrote summary plot: {out_png}")


def main():
    p = argparse.ArgumentParser(
        description="Extract .cif.gz and compute per-atom nearest-chain distances."
    )
    p.add_argument("--input-dir", required=True, type=Path, help="Directory with .cif.gz files.")
    p.add_argument(
        "--extracted-dir",
        required=True,
        type=Path,
        help="Directory to write decompressed .cif files.",
    )
    p.add_argument(
        "--out-dir",
        required=True,
        type=Path,
        help="Directory to write output CSVs.",
    )
    p.add_argument(
        "--atom",
        dest="atoms",
        action="append",
        required=True,
        help="Atom to track in format CHAIN:RESNUM:ATOMNAME. Can be passed multiple times.",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Re-decompress and overwrite existing decompressed files.",
    )
    args = p.parse_args()

    # Decompress
    if args.force:
        # Remove any existing .cif in extracted dir (only those that match .cif.gz sources)
        for pth in args.extracted_dir.rglob("*.cif"):
            pth.unlink()

    cif_entries = decompress_cif_gz(args.input_dir, args.extracted_dir)
    if not cif_entries:
        raise SystemExit(f"No .cif.gz files found in {args.input_dir}")

    atom_specs = [parse_atom_spec(a) for a in args.atoms]

    all_rows = []

    parser = MMCIFParser(QUIET=True)

    for cif_path, cfg_cat in sorted(cif_entries, key=lambda x: str(x[0])):
        try:
            structure = parser.get_structure(cif_path.name, str(cif_path))
        except Exception as e:
            print(f"WARNING: Failed to parse {cif_path}: {e}")
            continue

        for chain_id, resnum, atom_name in atom_specs:
            atom, found_chain = find_atom(structure, chain_id, resnum, atom_name)
            if atom is None:
                row = {
                    "cif_file": cif_path.name,
                    "cif_path": str(cif_path),
                    "cfg_category": cfg_cat,
                    "atom_spec": f"{chain_id}:{resnum}:{atom_name}",
                    "nearest_chain": "",
                    "nearest_resnum": "",
                    "nearest_atom": "",
                    "distance": float("nan"),
                }
                all_rows.append(row)
                continue

            other_atoms = get_all_other_chain_atoms(structure, found_chain)
            dist, nearest_chain, nearest_resnum, nearest_atom = compute_nearest(atom, other_atoms)

            row = {
                "cif_file": cif_path.name,
                "cif_path": str(cif_path),
                "cfg_category": cfg_cat,
                "atom_spec": f"{chain_id}:{resnum}:{atom_name}",
                "nearest_chain": nearest_chain,
                "nearest_resnum": nearest_resnum,
                "nearest_atom": nearest_atom,
                "distance": dist,
            }
            all_rows.append(row)

    # Write master CSV
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    master_csv = out_dir / "distances_all.csv"
    fieldnames = [
        "cif_file",
        "cif_path",
        "cfg_category",
        "atom_spec",
        "nearest_chain",
        "nearest_resnum",
        "nearest_atom",
        "distance",
    ]
    write_csv(master_csv, all_rows, fieldnames)
    print(f"Wrote master distances CSV: {master_csv}")

    # Split into per-category CSVs
    by_cat = {}
    for r in all_rows:
        cat = r["cfg_category"]
        by_cat.setdefault(cat, []).append(r)

    for cat, rows in by_cat.items():
        cat_csv = out_dir / f"distances_cfg{cat}.csv"
        write_csv(cat_csv, rows, fieldnames)

    print(f"Wrote {len(by_cat)} category CSV(s) under {out_dir}")

    # Summary per category + atom_spec
    summary_rows = []
    for (cat, atom_spec), group in {
        (r["cfg_category"], r["atom_spec"]): [] for r in all_rows
    }.items():
        pass

    # Build grouped stats (mean + median) for each (category, atom_spec)
    stats = {}
    for r in all_rows:
        cat = r["cfg_category"]
        atom_spec = r["atom_spec"]
        key = (cat, atom_spec)
        stats.setdefault(key, []).append(r.get("distance"))

    for (cat, atom_spec), dists in stats.items():
        arr = np.array([d for d in dists if np.isfinite(d)])
        summary_rows.append(
            {
                "cfg_category": cat,
                "atom_spec": atom_spec,
                "n_points": int(len(arr)),
                "mean_distance": float(np.nan) if arr.size == 0 else float(np.mean(arr)),
                "median_distance": float(np.nan) if arr.size == 0 else float(np.median(arr)),
            }
        )

    summary_csv = out_dir / "summary_by_cfg_and_atom.csv"
    write_csv(
        summary_csv,
        summary_rows,
        ["cfg_category", "atom_spec", "n_points", "mean_distance", "median_distance"],
    )
    print(f"Wrote summary CSV: {summary_csv}")

    # --- plotting (optional) ---
    if _HAS_MATPLOTLIB:
        try:
            plot_summary(summary_rows, out_dir)
        except Exception as e:
            print(f"WARNING: Failed to plot summary: {e}")
    else:
        print("matplotlib not installed; skipping plot generation.")


if __name__ == "__main__":
    main()
