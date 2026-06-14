#!/usr/bin/env python3
"""Build a one-row metadata parquet so RFD3 trains on a SINGLE structure.

Day 6 / Exercise 4 (course 27666).

The RFD3 dataloader does not read structure files directly — it reads a *metadata
parquet* with one row per training example, and each row tells AtomWorks which structure
file to open. To train on one structure, we write a parquet with exactly one row.

We mimic foundry's `monomer_distillation` dataset, which is parsed by
`atomworks.ml.datasets.parsers.GenericDFParser`. That parser needs only two columns:

    example_id   unique id for the example (any unique string)
    path         absolute path to a structure file (.cif recommended, .pdb works)

With `pn_unit_iid_colnames=null` the parser crops the structure at a random location and
loads assembly "1" — exactly what we want for a single monomer.

Usage
-----
    python make_single_structure_parquet.py \
        --structure /abs/path/to/1qys.cif \
        --out-dir   /abs/path/to/single_structure_data \
        --example-id top7_1qys

This writes:
    <out-dir>/af2_distillation_facebook.parquet   # the one-row metadata parquet

Then point foundry at <out-dir> via the `single_structure.yaml` experiment config
(see Exercise 5), or override on the CLI:
    paths.data.monomer_distillation_parquet_dir=<out-dir>

Requirements: pandas + pyarrow (both already in the course `protein-design` env).
Optional residue-count check uses atomworks.io if available.

Run inside the course environment:
    source /dtu/blackhole/00/c27666/miniforge/bin/activate && conda activate protein-design
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import pandas as pd

# foundry's monomer dataset expects this exact filename inside the parquet dir
# (see configs/datasets/train/rfd3_monomer_distillation.yaml). Keeping the name
# means you only have to override the *directory* path.
PARQUET_FILENAME = "af2_distillation_facebook.parquet"


def count_residues(structure_path: Path) -> int | None:
    """Best-effort residue count, for the ~50-residue sanity check. Returns None if
    AtomWorks isn't importable here."""
    try:
        from atomworks.io import parse

        out = parse(str(structure_path))
        atom_array = out["assemblies"]["1"][0]
        # number of distinct (chain, residue) groups
        n = len(set(zip(atom_array.chain_id, atom_array.res_id)))
        return n
    except Exception as exc:  # noqa: BLE001 - this is just an optional convenience
        print(f"  (skipping residue count: {type(exc).__name__}: {exc})")
        return None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--structure", required=True, help="Absolute path to the .cif/.pdb file to train on")
    ap.add_argument("--out-dir", required=True, help="Directory to write the parquet into")
    ap.add_argument("--example-id", default=None, help="Unique id for the example (default: file stem)")
    args = ap.parse_args()

    structure_path = Path(args.structure).expanduser().resolve()
    if not structure_path.exists():
        raise SystemExit(f"Structure file not found: {structure_path}")

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    example_id = args.example_id or structure_path.stem

    # ---- the one row -------------------------------------------------------
    df = pd.DataFrame(
        [
            {
                "example_id": example_id,
                "path": str(structure_path),  # absolute path -> no base_path needed
            }
        ]
    )

    out_path = out_dir / PARQUET_FILENAME
    df.to_parquet(out_path, index=False)

    print("Wrote single-structure metadata parquet:")
    print(f"  {out_path}")
    print(df.to_string(index=False))

    n_res = count_residues(structure_path)
    if n_res is not None:
        flag = "  <-- nice and small" if 20 <= n_res <= 120 else "  <-- larger than ideal; set crop_size above this"
        print(f"\nResidue count: {n_res}{flag}")

    print("\nNext: set the monomer parquet directory to this folder, e.g.")
    print(f"  paths.data.monomer_distillation_parquet_dir={out_dir}")


if __name__ == "__main__":
    main()
