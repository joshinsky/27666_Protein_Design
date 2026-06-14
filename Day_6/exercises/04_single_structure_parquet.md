# Exercise 4 — Recompute the parquet for a single ~50-residue structure

**Goal:** produce the metadata file that makes RFD3 train on **one** structure, and nothing
else. From Exercise 3 you know the dataloader reads a **parquet** (one row per example).
Here you write a one-row parquet.

## Which dataset to mimic

The PDB pn_unit dataset (`experiment=pretrain`) expects a rich metadata schema (cluster ids,
pn_unit_iids, deposition dates, …) that only makes sense for the full PDB. **Don't fight it.**

foundry has a much simpler dataset built for exactly this shape of data — the
**monomer-distillation** dataset
(`configs/datasets/train/rfd3_monomer_distillation.yaml`). The bulk *distillation data*
referenced by that config is **not publicly available** — but that doesn't matter to us. We
are only borrowing its **wiring** (the `PandasDataset` + `GenericDFParser` combination) and
pointing it at our **own** one-structure parquet and our **own** downloaded PDB.

Open the config and confirm (these are the facts that make this exercise easy):

- It uses `atomworks.ml.datasets.PandasDataset`.
- Its parser is `atomworks.ml.datasets.parsers.GenericDFParser` with
  `pn_unit_iid_colnames: null` → **crops at a random location, loads assembly `1`**.
- `columns_to_load:` is just **`example_id`** and **`path`**.

So a single-structure parquet needs **two columns**: a unique `example_id` and an absolute
`path` to a structure file. That's the whole schema.

## Step 1 — download an interesting small protein

We'll use **Top7** (`1QYS`) — the first de novo *designed* protein (Kuhlman & Baker, 2003),
a fitting subject for a design course. It's a ~92-residue α/β monomer.

```bash
mkdir -p single_structure_data
curl -L -o single_structure_data/1qys.cif https://files.rcsb.org/download/1QYS.cif
```

> Top7 is ~92 residues — a bit longer than 50, so it overfits slightly slower but is still
> tiny. If you'd rather have a faster run, swap in a ~40–55-residue single-chain protein
> such as `1ENH` (engrailed homeodomain, 54 aa) or `1VII` (villin headpiece, 36 aa):
> `curl -L -o single_structure_data/1enh.cif https://files.rcsb.org/download/1ENH.cif`.
>
> mmCIF is preferred by AtomWorks; a `.pdb` file usually also works. Remember the modelled
> chain length so you can set `crop_size` larger than it in Exercise 5 (so the structure is
> never cropped away).

## Step 2 — build the one-row parquet

Use the helper in `../templates/make_single_structure_parquet.py`:

```bash
python Day_6/templates/make_single_structure_parquet.py \
    --structure "$PWD/single_structure_data/1qys.cif" \
    --out-dir   "$PWD/single_structure_data" \
    --example-id top7_1qys
```

This writes `single_structure_data/af2_distillation_facebook.parquet` — the same filename
foundry's monomer dataset expects, so you only have to override the *directory* later.

Inspect it:

```bash
python -c "import pandas as pd; print(pd.read_parquet('single_structure_data/af2_distillation_facebook.parquet'))"
```

You should see exactly one row with your `example_id` and the absolute `path`.

## Step 3 — add the validation input (so you can watch it learn)

In Exercise 6 you will *watch* the model generate structures during training. The validation
step generates a protein from a small RFD3 input JSON (the same kind of contig JSON you used
on Days 3–4). Copy the template into the **same** data folder:

```bash
cp Day_6/templates/monomer.json "$PWD/single_structure_data/monomer.json"
cat "$PWD/single_structure_data/monomer.json"
```

It asks RFD3 to generate one **unconditional 92-residue monomer** (`"contig": "92-92"`,
no input structure). Because you will train *only* on Top7, the model's unconditional
samples should drift toward Top7-like folds as training proceeds — that's the payoff in
Exercise 6.

> So `single_structure_data/` ends up holding **two** files: the training parquet
> (`af2_distillation_facebook.parquet`) and the validation input (`monomer.json`).

### Discovery sub-task

Open `GenericDFParser` in
`atomworks/ml/datasets/parsers/default_metadata_row_parsers.py`. Answer:
- What does it return when `pn_unit_iid_colnames` is `None`? (→ where does it crop?)
- What happens to any **extra** columns you put in the parquet? (→ the `extra_info` key.)

## Checkpoint

- `single_structure_data/af2_distillation_facebook.parquet` exists and has **one row**.
- `path` is **absolute** and the file at that path exists.
- `single_structure_data/monomer.json` exists.
- (If the script printed a residue count) Top7 is ~92 residues.

## Why this counts as "recomputing the parquet"

The full PDB parquet is *computed* by AtomWorks from the entire PDB (`atomworks setup
metadata`). You have computed the minimal equivalent — a metadata table — for a dataset of
size one. Same role in the pipeline, one row instead of millions.
