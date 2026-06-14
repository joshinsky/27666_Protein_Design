# Exercise 6 — Watch it learn (trash → Top7)

**Goal:** see, with your own eyes, the model go from producing garbage at initialisation to
producing a Top7-like fold. This is the point of the whole day.

> All generation happens **inside the GPU training job** you submitted in Exercise 5 — you do
> not (and cannot) run anything on a GPU interactively. Here you monitor that job from a CPU
> interactive node and inspect the structures it writes out.

## Why you can watch it at all

Your `single_structure.yaml` turned on three things:
- `prevalidate: True` — the trainer runs a **validation pass before training**, generating a
  structure from the *random initial weights*. This is your "step 0 = trash" reference.
- `validate_every_n_epochs: 1` with a tiny `n_examples_per_epoch` — validation (= generating
  a fresh unconditional 92-mer from `monomer.json`) runs frequently as training proceeds.
- `checkpoint_every_n_epochs: 1` — a checkpoint is saved each epoch.

Because you train *only* on Top7, the model's unconditional output distribution collapses
toward Top7 — so successive validation structures should look more and more Top7-like.

## Step 1 — watch the loss live (CPU node)

While the job runs, follow its log and the metrics:

```bash
bjobs
tail -f day6_train_<job-id>.out          # loss + validation messages stream here
```

If you enabled W&B (Exercise 2), open the run at wandb.ai and watch the loss curve. Otherwise
the CSV logger writes metrics under your `paths.log_dir` run folder — plot it at the end:

```bash
# find the run dir, then plot the training-loss column from the CSV with pandas/matplotlib
ls -R logs/ | head
```

**Expectation:** the training loss falls steeply in the first hundreds of steps and
plateaus. A million-parameter model on one example *should* nearly memorise it. A flat/high
loss means something upstream is wrong (go back to the Exercise 5 dry-run).

## Step 2 — find the generated structures

The trainer writes its run outputs under your run's `output_dir` (derived from
`paths.log_dir`). Explore it and locate **(a)** the validation design structures and
**(b)** the saved checkpoints:

```bash
RUN=$(ls -dt logs/*/ | head -1)    # most recent run dir
find "$RUN" -maxdepth 3 -type f \( -name "*.pdb" -o -name "*.cif" \) | head
find "$RUN" -maxdepth 3 -type d -iname "*ckpt*" -o -iname "*valid*" 2>/dev/null
```

> **Discovery task:** the exact folder layout (where validation designs land, how epochs are
> named) is something you confirm by looking. Note the path of the **pre-validation** design
> (random weights) and a **late-epoch** design.

## Step 3 — look at them

Structures are easiest to view off the cluster. Copy a few down to your own machine and open
them in PyMOL (or ChimeraX), alongside the real Top7:

```bash
# run on YOUR computer
scp -r <your-id>@transfer.gbar.dtu.dk:./foundry/logs/<run>/<...>/ ./day6_designs
scp <your-id>@transfer.gbar.dtu.dk:./single_structure_data/1qys.cif ./
```

In PyMOL, load the **pre-validation** design, an **early** one, a **late** one, and `1qys`:

- **Pre-validation (random weights):** extended / tangled / blob — no secondary structure.
- **Mid training:** secondary structure appears; a rough globular shape.
- **Late training:** a compact α/β monomer that should resemble Top7's fold.
- Superpose a late design on `1qys` (`align` / `super`) and look at the RMSD trend.

## Checkpoint

- You can point to a **loss curve that decreased**.
- You can show **at least two generated structures** — an early "trash" one and a later
  Top7-like one — and describe the difference.

## Reflection (wrap-up discussion)

- Why do we *want* the model to overfit here, when overfitting is normally bad?
- The model never saw a contig or a hint — it generated unconditionally. Why does training on
  one structure make unconditional samples converge to that structure?
- What would you change to train on **10** structures? On all of the PDB? (Hint: the parquet
  gets more rows; the sampler weights and filters in
  `configs/datasets/train/pdb/` start to matter.)
- Where would you add a new **conditioning** task? (Hint: Exercise 3's transform pipeline +
  `configs/datasets/design_base.yaml` → `train_conditions`.)
