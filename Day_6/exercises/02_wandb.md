# Exercise 2 — (Optional) Weights & Biases API key

**Goal:** be able to watch the training loss curve live in a browser. This is **optional** —
training works without it (foundry defaults to a local CSV logger).

## Why bother

The whole point of today's run is to *watch a loss go down*. W&B gives you a live curve with
no extra code. The CSV logger writes the same numbers to a file you can plot yourself.

## Task (optional)

1. Make a free account at https://wandb.ai and copy your API key from
   https://wandb.ai/authorize
2. Authenticate once (do this on the interactive node, in the activated env):
   ```bash
   export WANDB_API_KEY=<your-key>     # or: wandb login
   ```
   To make it persist into your submitted job, add the `export WANDB_API_KEY=...` line to
   your submit script (see `templates/submit_train.sh`), or `wandb login` once so the key is
   cached in your home directory.
3. foundry selects the logger via the `logger=` override:
   ```bash
   # with W&B:
   python models/rfd3/src/rfd3/train.py experiment=single_structure logger=wandb
   # without (default): local CSV
   python models/rfd3/src/rfd3/train.py experiment=single_structure logger=csv
   ```

## If you skip W&B

Use `logger=csv` (the default). Metrics are written under the run's output directory
(see `configs/paths/` for `log_dir`/`output_dir`). You can plot the CSV with pandas/matplotlib
at the end of Exercise 5/6.

## Checkpoint

- (W&B) `wandb login` reports you are logged in, **or**
- (CSV) you know where the run's metrics CSV will be written.

> Privacy note: a W&B run uploads your config and metrics to wandb.ai. For a throwaway
> single-structure run this is harmless, but don't upload anything you consider private.
