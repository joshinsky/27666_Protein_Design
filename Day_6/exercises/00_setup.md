# Exercise 0 — Environment & clone

**Goal:** get onto a GPU node with the course environment active and a copy of foundry.

You do **not** install anything today — the course environment already has RFD3, foundry,
AtomWorks, PyTorch, Lightning and Hydra. You only need to (a) activate it and (b) clone the
foundry repo so you have the training code and configs.

> Branch note: foundry's default branch is **`production`** (not `main`). All paths and
> commands below were checked against `production`.

## Task

1. **Log in and move off the login node** (same as Day 1):
   ```bash
   ssh <your-id>@login1.hpc.dtu.dk
   linuxsh
   ```

2. **Activate the course environment:**
   ```bash
   source /dtu/blackhole/00/c27666/miniforge/bin/activate
   conda activate protein-design
   ```
   Your prompt should now start with `(protein-design)`.

   > If that path doesn't work, try the Day 1 form:
   > `source /dtu/blackhole/00/c27666/miniforge3/etc/profile.d/conda.sh && conda activate protein-design`

3. **Check the training stack is importable:**
   ```bash
   python -c "import rfd3, foundry, atomworks, torch, lightning, hydra; print('ok')"
   ```
   If this prints `ok`, the environment has everything you need.

4. **Clone foundry** (you need the repo for the configs and `train.py`, even though the
   package is already installed):
   ```bash
   git clone https://github.com/RosettaCommons/foundry.git
   cd foundry
   ```

## Checkpoint

- Prompt shows `(protein-design)`.
- `python -c "import rfd3, atomworks, lightning, hydra; print('ok')"` prints `ok`.
- You have a `foundry/` checkout and are sitting in it.

## Notes / gotchas

- **Run everything with `python` from the foundry repo root.** The training script uses
  `rootutils` + the `.project-root` marker to set `PROJECT_ROOT` and add the repo to the
  Python path, so running from the repo root makes it use *this* checkout's code and configs.
  (Earlier foundry docs say `uv run python …`; on the HPC we use the conda `python` instead —
  the dependencies are already in the `protein-design` env.)
- **Do not** run `./train.py` directly — its shebang points at an internal helper. Always
  launch as `python models/rfd3/src/rfd3/train.py ...`.
- The heavy training itself goes to a **GPU node via `bsub`** (Exercise 5), not the
  interactive node. The interactive node is fine for cloning, editing configs, and the import
  check above.
