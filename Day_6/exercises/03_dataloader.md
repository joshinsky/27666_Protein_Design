# Exercise 3 — Find the dataloader and the dataset "parquet"

**Goal:** trace, from the training config down to disk, **exactly what file RFD3 reads to
decide which structures to train on**. That file is a **parquet** of metadata — one row per
training example — and recomputing it for a single structure is Exercise 4.

This is the conceptual core of the day. Take your time reading the YAML.

## Background: two different things both called "the dataloader"

1. **The PyTorch `DataLoader`** — batching/worker config. In foundry:
   `models/rfd3/configs/dataloader/default.yaml` (`batch_size`, `num_workers`,
   `prefetch_factor`). Boring but real.
2. **The AtomWorks `Dataset`** — the thing that, given an index, returns *which structure*
   and *which chains/interface* to load, parses the structure file into an `AtomArray`, and
   runs the transform pipeline. This is configured under
   `models/rfd3/configs/datasets/`.

The Dataset is what matters for "train on one structure".

## Task — trace the config chain

Start at the experiment and follow the `defaults:` lists down. Open these in order and note
what each adds:

```
configs/experiment/pretrain.yaml          # sets datasets.train.pdb.probability = 1.0
  └─ configs/datasets/design_base.yaml     # pulls in the PDB sub-datasets + val + conditions
       └─ configs/datasets/train/pdb/rfd3_train_pn_unit.yaml
            └─ .../pdb/af3_train_pn_unit.yaml   # <-- the parquet path + columns + filters
                 └─ .../pdb/pdb_base.yaml → base.yaml → base_no_weights.yaml
```

Answer:

1. In `af3_train_pn_unit.yaml`, **what is the `dataset.dataset.data` value?** (It is the
   parquet path, written with a Hydra interpolation.)
2. What **`_target_`** class parses it? (Look for `dataset_parser._target_` and the
   `dataset._target_`.)
3. Where does the interpolation `${paths.data.pdb_parquet_dir}` resolve to? Open
   `configs/paths/data/default.yaml`.
4. List the `filters:` applied to the parquet. Which one would **drop a brand-new custom
   structure** that has no cluster assigned? (Hint: `cluster.notnull()`.)
5. What are the `columns_to_load`? These are the columns your single-structure parquet will
   need to contain (or you must change the config).

## Checkpoint — answer key

1. `data: ${paths.data.pdb_parquet_dir}/pn_units_df_train.parquet`
2. The dataframe is parsed by `atomworks.ml.datasets.parsers.PNUnitsDFParser`
   (`base_dir: ${paths.data.pdb_data_dir}`), wrapped by
   `atomworks.ml.datasets.StructuralDatasetWrapper` around an
   `atomworks.ml.datasets.PandasDataset` (`id_column: example_id`). The structure files
   themselves are read from `paths.data.pdb_data_dir`.
3. `configs/paths/data/default.yaml` sets `pdb_parquet_dir` (and `pdb_data_dir`) to
   **hard-coded internal IPD paths** (e.g. `/projects/ml/...`). **These will not exist on
   your machine — you must override them.** This is the single most common reason the run
   fails to start. ⚠️
4. `cluster.notnull()` — a custom structure with no cluster id is filtered out. You will
   either give your row a dummy `cluster` value or drop this filter.
5. `example_id, pdb_id, assembly_id, deposition_date, resolution, num_polymer_pn_units,
   method, cluster, n_prot, n_nuc, n_ligand, n_peptide,
   total_num_atoms_in_unprocessed_assembly, q_pn_unit_iid,
   q_pn_unit_non_polymer_res_names, all_pn_unit_iids_after_processing, q_pn_unit_is_loi`.

## What a "parquet row" means

Each row = one training example. For the PDB pn_unit dataset, a row says: *for PDB
`pdb_id`, assembly `assembly_id`, train on the polymer unit `q_pn_unit_iid`*. The parser
opens the structure from `pdb_data_dir`, crops around that unit, and feeds it through the
transform pipeline. To train on **one** structure you need **one** valid row pointing at a
structure file you control.

See AtomWorks' own walkthrough of datasets/parquets:
https://rosettacommons.github.io/atomworks/latest/auto_examples/dataset_exploration.html
