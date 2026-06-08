# rf3_metrics_foundry.py
#
# Replacement for rf3_metrics.py for the rc-foundry RF3 output format.
# RC-foundry RF3 writes *_summary_confidences.json instead of *.score files.
#
# summary_confidences.json keys:
#   chain_ptm          : list[float]  per-chain pLDDT, indexed by chain order
#   chain_pair_pae_min : list[list]   N×N min interface PAE matrix
#   chain_pair_pae     : list[list]   N×N mean interface PAE matrix
#   chain_pair_pde_min : list[list]   N×N min interface PDE matrix
#   overall_plddt      : float
#   overall_pae        : float
#   overall_pde        : float
#   ptm                : float        predicted TM-score
#   iptm               : float        interface pTM-score
#   has_clash          : bool
#   ranking_score      : float

import os
import glob
import json
import numpy as np
import pandas as pd


def _load_summary(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def gather_rf3_metrics_foundry(
    parent: str,
    binder_chain_idx: int = 0,
    target_chain_idxs: list | None = None,
    out_csv: str | None = None,
) -> pd.DataFrame:
    """Gather metrics from rc-foundry RF3 *_summary_confidences.json files.

    Args:
        parent            : root directory of rf3_out (searches recursively)
        binder_chain_idx  : index of the binder chain in the chain_ptm list (default 0)
        target_chain_idxs : list of target chain indices for interface PAE columns;
                            None = all non-binder chains
        out_csv           : optional path to write the CSV

    Returns:
        DataFrame with one row per design, columns:
            design_id, overall_plddt, binder_plddt, ptm, iptm,
            ranking_score, has_clash,
            pae_binder_vs_chainN  (one column per target chain index)
    """
    parent = os.path.abspath(parent)
    json_files = sorted(
        glob.glob(os.path.join(parent, "**", "*_summary_confidences.json"),
                  recursive=True)
    )

    # Prefer the top-level copy (best model) over per-sample files
    # Top-level files sit directly inside a subdirectory named after the design.
    top_level = [
        p for p in json_files
        if os.path.basename(p) == f"{os.path.basename(os.path.dirname(p))}_summary_confidences.json"
    ]
    if top_level:
        json_files = top_level

    if not json_files:
        raise FileNotFoundError(
            f"No *_summary_confidences.json files found under: {parent}"
        )

    records = []
    for p in json_files:
        try:
            sc = _load_summary(p)
        except Exception as e:
            print(f"[WARN] Could not read {p}: {e}")
            continue

        design_id = os.path.basename(os.path.dirname(p))
        n_chains   = len(sc.get("chain_ptm", []))
        b_idx      = binder_chain_idx
        t_idxs     = target_chain_idxs if target_chain_idxs is not None \
                     else [i for i in range(n_chains) if i != b_idx]

        row = {
            "design_id":     design_id,
            "overall_plddt": sc.get("overall_plddt", np.nan),
            "binder_plddt":  sc["chain_ptm"][b_idx] if n_chains > b_idx else np.nan,
            "ptm":           sc.get("ptm",           np.nan),
            "iptm":          sc.get("iptm",          np.nan),
            "ranking_score": sc.get("ranking_score", np.nan),
            "has_clash":     sc.get("has_clash",     np.nan),
        }

        pae_min = sc.get("chain_pair_pae_min", [])
        for t_idx in t_idxs:
            try:
                val = pae_min[b_idx][t_idx]
            except (IndexError, TypeError):
                val = np.nan
            row[f"pae_binder_vs_chain{t_idx}"] = val

        records.append(row)

    df = pd.DataFrame(records)

    if out_csv:
        os.makedirs(os.path.dirname(os.path.abspath(out_csv)), exist_ok=True)
        df.to_csv(out_csv, index=False)
        print(f"Wrote: {out_csv}")

    print(f"Found: {len(json_files)}   Parsed: {len(df)}")
    return df
