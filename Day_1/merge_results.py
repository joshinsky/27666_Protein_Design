#!/usr/bin/env python3
"""Merge the per-target CSVs from the array run into one table + plot.

Run after all tm_array tasks have finished (check with bjobs):
    python merge_results.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

PARTS = Path("results/parts")
OUT = Path("results")

parts = sorted(PARTS.glob("part_*.csv"))
if not parts:
    raise SystemExit(f"No part_*.csv files in {PARTS}")

df = (pd.concat([pd.read_csv(p) for p in parts], ignore_index=True)
        .sort_values("TM (norm. by reference)", ascending=False)
        .reset_index(drop=True))

csv_path = OUT / "tm_results.csv"
df.to_csv(csv_path, index=False)
print(df.to_string(index=False))
print(f"Saved {csv_path}")

plt.figure(figsize=(8, 4))
plt.bar(df["target"], df["TM (norm. by reference)"])
plt.axhline(0.5, linestyle="--", label="0.5 (same-fold threshold)")
plt.ylabel("TM-score (normalized by reference)")
plt.title("TM-score vs reference")
plt.xticks(rotation=45, ha="right")
plt.legend()
plt.tight_layout()
plt.savefig(OUT / "tm_scores.png", dpi=150)
print(f"Saved {OUT / 'tm_scores.png'}")
