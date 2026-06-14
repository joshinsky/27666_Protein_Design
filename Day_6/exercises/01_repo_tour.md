# Exercise 1 — Repo tour: find the RFD3 training code

**Goal:** build a mental map of where training, configs, and data code live. This is a
**reading** exercise — write down the file paths, you will use them in every later step.

## Task

The RFD3 model is one package under `models/`. Explore:

```bash
ls models/rfd3
ls models/rfd3/src/rfd3
ls models/rfd3/configs
```

Answer these (write the path next to each):

1. **Where is the training entry point** (the script you launch)?
2. **What configuration system** does it use? (Hint: look at the imports and the
   `configs/` tree — note the `@hydra.main` decorator and `configs/train.yaml`.)
3. **Where are the "experiments"** — the named config bundles you pass as
   `experiment=<name>`?
4. **Where are the dataset and dataloader configs?**
5. **Where are the model and trainer configs?**

foundry is built on **Hydra**: you compose a run from layered YAML configs and override
any value from the command line (`key=value`). `experiment=pretrain` means "apply
`configs/experiment/pretrain.yaml` on top of the base config".

### Read the README training section

Open `models/rfd3/README.md` and find the **"Training and Fine-Tuning"** section. Note the
canonical launch command — you will adapt it in Exercise 5:

```bash
python models/rfd3/src/rfd3/train.py experiment=pretrain ckpt_path=<path/to/ckpt>
```

and the key fact that decides Exercise 4–5:

> Supplying `ckpt_path=null` (default) will start with **fresh weights**.

## Checkpoint — answer key

Confirm your answers against these (paths relative to repo root):

| Question | Answer |
|---|---|
| Training entry point | `models/rfd3/src/rfd3/train.py` |
| Config system | Hydra; root config `models/rfd3/configs/train.yaml` |
| Experiments | `models/rfd3/configs/experiment/` (`pretrain.yaml`, `debug.yaml`, …) |
| Dataset configs | `models/rfd3/configs/datasets/` ; dataloader `configs/dataloader/{default,fast}.yaml` |
| Model / trainer configs | `models/rfd3/configs/model/` and `configs/trainer/` |
| Data paths | `models/rfd3/configs/paths/` (and `paths/data/default.yaml`) |

## Tip — print the resolved config

`train.py` prints the fully-resolved config tree at startup (`print_config_tree`). This is
your single best debugging tool today: any time you are unsure whether an override landed,
launch and read the printed tree. You can also dry-run the config without training using
Hydra's `--cfg job`:

```bash
python models/rfd3/src/rfd3/train.py experiment=pretrain --cfg job | less
```

(Run this on the interactive node just to print config — it does not train.)
