# Day 1 - TM-align on the HPC (batch jobs)

This is the **batch-job guide**. For the interactive walkthrough, open the notebook `tm_compare_batch.ipynb` instead.

Compare **one reference structure** against **all structures in a target folder** using [`tmtools`](https://pypi.org/project/tmtools/) (a Python wrapper
around TM-align). 
Each `.pdb` file is assumed to hold a **single chain** (e.g. VHH structures prepared from SAbDab); the first chain is read.

There are **two ways to run the same analysis**:

1. **Interactive** - `tm_compare_batch.ipynb`. Run it cell by cell to explore
   and see the table/plot inline. Best for understanding what the analysis does.
   
2. **Batch on the HPC (LSF)** - the same logic as a script you submit to the
   cluster with `bsub`. This is what the rest of *this* guide teaches.

The batch route comes in **two flavours** so you can learn both submission
patterns:

| Route | Script | Submit script | When |
|-------|--------|---------------|------|
| Single job | `tm_compare.py` | `submit_tm.sh` | One job loops over all targets. Right choice for this exercise. |
| Job array | `tm_compare_array.py` + `merge_results.py` | `submit_tm_array.sh` | One task **per target**, run in parallel, then merged. Not required approach for just 10 targets - included to teach the pattern and to scale to hundreds or thousands. |

---

## Folder layout

```
Day_1/
├── README.md                  # short landing note (notebook + batch pointers)
├── README_batch.md            # this guide - the batch-job instructions
├── tm_compare_batch.ipynb     # interactive notebook
├── tm_compare.py              # single-job script
├── tm_compare_array.py        # array worker (one target per task)
├── merge_results.py           # merges array outputs into one table + plot
├── submit_tm.sh               # LSF submit - single job
├── submit_tm_array.sh         # LSF submit - job array
├── environment.yml            # conda environment
├── data/
│   ├── input_vhh/             # the ONE reference (4s11.pdb)
│   └── target_vhh/            # the 10 target .pdb files
└── results/                   # created on first run (CSV + plot)
```

All scripts default to `data/input_vhh` and `data/target_vhh`, so they work against this folder with **no path edits**.

---

## 0. Setup (on a login node)

**You probably don't need to set anything up.** The submit scripts point to the shared course environment for 27666:

```
/dtu/blackhole/00/c27666/miniforge3  ->  conda env "protein-design"
```
So once it's on the cluster you can go straight to submitting a job.


### If you do NOT want to use the shared environment

Build your own conda environment once (it will be called `tmenv`):

```sh
module load miniconda3            # or your usual conda init
conda env create -f environment.yml
conda env list                    # check that "tmenv" now appears
```

Then, in whichever submit script you use, change this line:

```sh
conda activate protein-design     # shared env (default)
```

to:

```sh
conda activate tmenv              # your own env
```

That is the only edit needed to switch. You build the environment once; after
that you just submit jobs as normal.

---

## Connecting and moving files

```sh
# log in
ssh <id>@login1.hpc.dtu.dk

# copy this folder up to the cluster (run locally)
scp -r Day_1 <id>@transfer.gbar.dtu.dk:./

# copy results back down afterwards (run locally)
scp -r <id>@transfer.gbar.dtu.dk:./Day_1/results ./
```

---

## Route 1 - Single job 

One `bsub` submission runs `tm_compare.py`, which loops over every target in sequence and writes the final CSV and plot itself.

```sh
cd Day_1
bsub < submit_tm.sh
```

Outputs land in `results/`: `tm_results.csv` and `tm_scores.png`.

---

## Route 2 - Job array

The scheduler expands `tm_array[1-10]` into 10 independent tasks. Each runs `tm_compare_array.py` for **one** target (selected by `$LSB_JOBINDEX`) and
writes a single-row CSV into `results/parts/`. When all tasks finish, you merge the parts into the final table.

```sh
cd Day_1
# the range [1-10] already matches the 10 targets in data/target_vhh.
# if you change the target set:  ls data/target_vhh/*.pdb | wc -l  -> N, edit [1-N]
bsub < submit_tm_array.sh

bjobs                 # wait until all tasks show DONE
python merge_results.py
```

Same `results/tm_results.csv` and `results/tm_scores.png` as Route 1.

---

## Monitoring jobs

```sh
bstat                 # overview of your jobs (single job or array)
bjobs                 # running / pending jobs
bjobs -l <job-id>     # detailed status of one job
```

---

## What you need to adjust

**Nothing, for course 27666.** The submit scripts already point to the shared `protein-design` environment, the data folders are in place, and the array
range matches the 10 targets. Just submit.

Two optional tweaks, only if you want them:

- **Emails** when the job starts/finishes: uncomment the `-u` / `-B` / `-N` lines in `submit_tm.sh` and put in your DTU address.
- **Your own environment** instead of the shared one: see the setup section
  above, then change `conda activate protein-design` to `conda activate tmenv`
  in the submit script.

(If you ever change the target set, also update the `[1-10]` range in
`submit_tm_array.sh` to match the new count.)

---
