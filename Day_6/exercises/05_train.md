# Exercise 5 — Reinitialise the weights and launch training

**Goal:** start a real RFD3 training run on your single structure, from **random weights**,
on a GPU node. In Exercise 6 you watch it learn.

## "Reinitialise the weights" — what that means here

RFD3's training script chooses between *continuing from a checkpoint* and *starting fresh*
from one config value. From `models/rfd3/README.md`:

> Supplying `ckpt_path=null` (default) will start with **fresh weights**.

So "reinitialise" = `ckpt_path=null`. The network is built and randomly initialised — you are
**not** loading the pretrained RFD3, you are training a brand-new model from scratch on
exactly one example. (Find where this happens: `trainer.construct_model()` in `train.py`, and
the checkpoint logic in `foundry.utils.weights`.)

## Step 1 — install the experiment config

From the foundry repo root, copy in the template config and the submit script:

```bash
cp ../27666_Protein_Design/Day_6/templates/single_structure.yaml \
   models/rfd3/configs/experiment/single_structure.yaml
cp ../27666_Protein_Design/Day_6/templates/submit_train.sh ./submit_train.sh
```
*(adjust the source path to wherever you cloned the course repo)*

Read `single_structure.yaml`. It: enables the monomer dataset, turns off the PDB datasets,
sets `ckpt_path: null`, shrinks the crop/batch, fixes `b_factor_min`, points all validation
datasets at your `monomer.json`, and turns on **frequent validation** with
`prevalidate: True` (Exercise 6).

## Step 2 — dry-run the config (do this before every real launch)

On the **interactive node**, resolve the config without training and read it:

```bash
DATA=$HOME/single_structure_data    # the folder from Exercise 4 (parquet + monomer.json)
python models/rfd3/src/rfd3/train.py \
    experiment=single_structure \
    paths.data.monomer_distillation_parquet_dir=$DATA \
    paths.data.monomer_distillation_data_dir=$DATA \
    paths.data.design_benchmark_data_dir=$DATA \
    --cfg job | less
```

Check in the printed config that:
- `ckpt_path: null`
- `datasets.train.monomer_distillation.probability: 1.0` and `...pdb.probability: 0.0`
- the monomer dataset's `data:` resolves to **your** parquet path
- the val datasets' `data:` resolve to **your** `monomer.json`
- `b_factor_min: 0` and `crop_size: 128`

> This dry-run plus the config tree `train.py` prints at startup are your debugging tools. If
> an override didn't land, fix the key name here — that's cheaper than discovering it after a
> job has queued and started. If a `defaults`-list key doesn't compose, see the fallback in
> `INSTRUCTOR_NOTES.md`.

## Step 3 — edit and submit the GPU job

Open `submit_train.sh` and set:
- `#BSUB -q <gpu-queue>` to the GPU queue named in the course materials.
- `DATA=...` to your `single_structure_data` folder.

Then submit from the foundry repo root:

```bash
bsub < submit_train.sh
```

Monitor exactly as in Day 1:

```bash
bjobs                          # PEND -> RUN -> DONE
tail -f day6_train_<job-id>.out
```

> One job, one GPU. Do **not** submit this as a job array — see the Day 1 GPU etiquette note.

## Checkpoint — what a successful launch looks like

- The job reaches `RUN` and the `.out` file shows the resolved config tree, then
  "Instantiating trainer", model construction, and a **pre-validation** pass (because
  `prevalidate: True`).
- Within a minute or two of training you see **training-loss** lines being logged (the
  `log_af3_training_losses_callback` logs every 25 steps).
- Getting here is most of the exercise: it means your parquet, your `monomer.json`, your
  path overrides, and the config all line up.

## Common failure modes (and the fix)

| Symptom | Cause | Fix |
|---|---|---|
| `FileNotFoundError` under `/projects/ml/...` or `/net/scratch/...` | hard-coded internal paths in `configs/paths/data/default.yaml` | override `paths.data.*` and `paths.log_dir` (the submit script does this) |
| Dataset has 0 examples | `b_factor_min: 70` rejecting a crystal structure | confirm `b_factor_min: 0` landed in the dry-run |
| Validation can't find a JSON | `design_benchmark_data_dir` not overridden, or `monomer.json` missing | point it at your `DATA` folder; confirm `monomer.json` is there |
| Structure gets cropped | `crop_size` < protein length | raise `crop_size` above your residue count |
| CUDA OOM | crop/batch too big for the GPU | lower `crop_size`, `max_atoms_in_crop`, `diffusion_batch_size_train` |
| `import` / module errors in the job | training deps missing from the env | re-run the Exercise 0 import check inside the job's env |

Once it's training and logging a loss, go to **Exercise 6** to watch it learn.
