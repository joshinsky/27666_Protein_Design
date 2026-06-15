# Day 6 — Design theory and methods

**27666**

Days 3–4 you *ran* RFdiffusion3 (RFD3) as a black box for binder and enzyme design.
Today you open the box. The goal is **method development**: clone the training
code, understand how data flows into the model, and **train RFD3 from scratch on a
single small protein** (we use Top7, the first de novo–designed protein) until it
memorises that one structure.

Overfitting one structure is a standard sanity check when developing a generative
model: if the training loss does not collapse toward zero on a single example, the
data pipeline or the model wiring is broken. It is the smallest possible end-to-end
training run, and it teaches the whole stack — dataloader, dataset metadata
(the "parquet"), weight initialisation, and the training loop.

> **What this is and isn't.** This is a learning exercise on the *real* RFD3 training
> code ([RosettaCommons/foundry](https://github.com/RosettaCommons/foundry)). You are
> not expected to produce a useful model — you are expected to make a single training
> run start, log a decreasing loss, **watch the model generate worse-then-better
> structures**, and be able to point at every component involved.

---

## Prerequisites

- The same **DTU HPC workflow as Day 1**: log in, `linuxsh` for interactive work, and
  `bsub < script.sh` to submit jobs. The interactive nodes are **CPU-only** — all GPU work
  (the training run) goes through a **submit script**.
- The **course environment** — no installation needed:
  ```bash
  source /dtu/blackhole/00/c27666/miniforge3/bin/activate
  conda activate protein-design
  ```
- Comfort with a Linux shell, `git`, editing YAML, and viewing structures in PyMOL.

You do **not** need the pretrained RFD3 checkpoint — you start from **fresh (random)
weights** (`ckpt_path=null`). Everything you do on a CPU interactive node (clone, edit
configs, build the parquet, dry-run the config with `--cfg job`); the actual training and
the structure generation run on a GPU via `bsub`.

---

## The exercises

Work through these in order. Each step lists a **task** (what to do) and a
**checkpoint** (how you know it worked). Full walkthrough with commands and the
discovery answers is in [`exercises/`](./exercises).

| # | Exercise | File |
|---|----------|------|
| 0 | Activate the course env and clone foundry | [exercises/00_setup.md](./exercises/00_setup.md) |
| 1 | Tour the repo — locate the RFD3 training code | [exercises/01_repo_tour.md](./exercises/01_repo_tour.md) |
| 2 | (Optional) Create a Weights & Biases API key | [exercises/02_wandb.md](./exercises/02_wandb.md) |
| 3 | Find the dataloader and the dataset "parquet" | [exercises/03_dataloader.md](./exercises/03_dataloader.md) |
| 4 | Recompute the parquet for a single structure (Top7) | [exercises/04_single_structure_parquet.md](./exercises/04_single_structure_parquet.md) |
| 5 | Reinitialise the weights and launch training (GPU job) | [exercises/05_train.md](./exercises/05_train.md) |
| 6 | Watch it learn — trash → Top7 | [exercises/06_watch_it_learn.md](./exercises/06_watch_it_learn.md) |

Supporting files live in [`templates/`](./templates):
- `make_single_structure_parquet.py` — helper to build a one-row metadata parquet.
- `single_structure.yaml` — a Hydra `experiment` config template for the training run.
- `monomer.json` — unconditional 92-mer validation input (so you can watch the model improve).
- `submit_train.sh` — LSF `bsub` submit script for the GPU training job.

---

## Instructor notes

Read [`exercises/INSTRUCTOR_NOTES.md`](./exercises/INSTRUCTOR_NOTES.md) before the
session. It covers the decisions you need to make (platform, pre-installed environment,
which structure, time budget) and the known gotchas (hard-coded internal paths in the
default config, the `cluster.notnull()` filter, validation datasets). Several steps are
deliberately left as **discovery tasks** for the students; the notes give the answers and
what to do if foundry's `production` branch has moved since this was written.
