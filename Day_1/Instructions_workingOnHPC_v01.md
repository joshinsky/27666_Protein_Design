# Working on the DTU HPC — running TM-align (Day 1)

How to connect to the DTU HPC cluster, use the shared course environment, and run the Day 1
structural-comparison job — interactively in the notebook, as a single batch job, or as a job
array.

> **Course 27666 · Protein Design · Day 1**

## Contents

1. [Log in to the cluster](#1-log-in-to-the-cluster)
2. [Move to an interactive node (`linuxsh`)](#2-move-to-an-interactive-node)
3. [Activate the shared environment](#3-activate-the-shared-environment)
4. [Get the files onto the cluster](#4-get-the-files-onto-the-cluster)
5. [Run the analysis (notebook, single job, or array)](#5-run-the-analysis)
6. [Watch the job live](#6-watch-the-job-live)
7. [Get an email when it finishes](#7-get-an-email-when-it-finishes)
8. [Where the results are, and bringing them back](#8-where-the-results-are-and-bringing-them-back)
9. [Optional: build your own environment](#9-optional--build-your-own-environment)
10. [Good to know](#10-good-to-know)

---

## 1. Log in to the cluster

Open a terminal on your own computer and connect over SSH. Replace `<your-id>` with your DTU
username (the part before *@dtu.dk*).

```sh
ssh <your-id>@login1.hpc.dtu.dk
```

Enter your DTU password when prompted. You are now on a **login node**.

#Setting up config file in VSCode for HPC

    Host DTU-HPC
    HostName login1.hpc.dtu.dk
    User x123456
    IdentityFile ~/.ssh/id_rsa
    ForwardAgent yes

## 2. Move to an interactive node

The login node is only for logging in — you may see a warning telling you not to run programs
there. Switch to an **interactive node** by typing:

```sh
linuxsh
```

This moves you to a shared interactive node where you can activate the environment, prepare files,
run quick checks, and submit jobs. Do this before the next steps.

> **Why:** the login node is shared by everyone just for logging in and light tasks. `linuxsh`
> gives you a proper node for interactive work. You will share it with other users, so keep heavy
> work to submitted jobs.

## 3. Activate the shared environment

The course provides a ready-made environment with everything the scripts need. Activate it:

```sh
source /dtu/blackhole/00/c27666/miniforge3/etc/profile.d/conda.sh
conda activate protein-design
```

Your prompt should now start with `(protein-design)`. Check the tools are there:

```sh
python -c "import tmtools; print('ok')"
```

If it prints `ok`, you are ready.

> **Note:** the submit scripts contain these same two lines, so a submitted job activates the
> environment on its own. Activating here is mainly for the quick check above.

## 4. Get the files onto the cluster

Cloning from GitHub directly on the cluster is simplest:

```sh
git clone https://github.com/DigBioLab/27666_Protein_Design.git
cd 27666_Protein_Design/Day_1
```

Or copy a folder up from your own machine (run this **on your computer**):

```sh
scp -r Day_1 <your-id>@transfer.gbar.dtu.dk:./
```

> **Two addresses:** use `login1.hpc.dtu.dk` to log in and work; use `transfer.gbar.dtu.dk` for
> `scp` file transfers. Same DTU login for both.

## 5. Run the analysis

There are **three ways** to run the same comparison — all produce the same scored table and plot.
Pick whichever suits you.

**Path A — Interactive notebook.** Open `tm_compare_batch.ipynb` and run it cell by cell. Best for
exploring and seeing the table and plot inline as you go. (Run it on an interactive node after
`linuxsh`, not on the login node.) The notebook saves `tm_results.csv` directly into `Day_1/` and
shows the plot inline (no PNG is saved) — a different location from the batch paths below, which
use a `results/` folder.

The other two paths submit the work to the cluster with `bsub`, from inside the `Day_1` folder.
Both write to `results/tm_results.csv` and `results/tm_scores.png`.

**Path B — Single batch job** (recommended) — runs over all targets in sequence:

```sh
bsub < submit_tm.sh
```

**Path C — Job array** — one task per target in parallel, then merge:

```sh
bsub < submit_tm_array.sh
# after all tasks finish:
python merge_results.py
```

> **The `<` matters:** `bsub < submit_tm.sh` hands the script to the scheduler, which reads the
> `#BSUB` lines and runs the work on a compute node. Submitting is fine from the login or
> interactive node — it does not run the work where you type it.

> **Which to use?** The notebook is for understanding the analysis interactively; the single batch
> job is the normal way to run it on the cluster; the job array is overkill for 10 targets and is
> included to teach the parallel-submission pattern (and to scale to hundreds of structures).
> Steps 6–8 below apply to the two batch paths.

## 6. Watch the job live

After submitting, check whether your job is pending (`PEND`), running (`RUN`), or finished
(`DONE`):

```sh
bstat                 # quick overview of your jobs
bjobs                 # running / pending jobs
bjobs -l <job-id>     # full detail on one job
```

To refresh the status automatically every 5 seconds (live view), use `watch` and stop it with
<kbd>Ctrl</kbd>+<kbd>C</kbd>:

```sh
watch -n 5 bjobs
```

You can also follow the job's printed output as it is written, by tailing the output file (the
name uses the job-id; for the array see `results/logs/`):

```sh
tail -f tm_compare_<job-id>.out
```

For the job array, wait until all tasks show `DONE` before running `merge_results.py`. If anything
fails, the `.err` file is where the reason appears.

## 7. Get an email when it finishes

The submit script can email you when the job starts and ends. Open `submit_tm.sh`, find these
lines near the top, remove one `#` from each (so they begin with a single `#`), and put in your
address:

```sh
### -- email at start (B) and end (N) --
#BSUB -u your_email@dtu.dk
#BSUB -B    # email when the job Begins
#BSUB -N    # email when the job is Done
```

Then submit as usual. You will get a start email and a completion email (with a short
resource-usage summary) at the address you set.

> **Tip:** in the file these lines start with `##BSUB` (two hashes = switched off). Removing one
> hash to leave `#BSUB` turns the option on.

## 8. Where the results are (and bringing them back)

When the job is `DONE`, the output is written into a `results/` folder inside `Day_1` **on the
cluster**:

```
Day_1/results/
├── tm_results.csv     # the scored table (ranked by TM-score)
└── tm_scores.png      # the bar chart
```

(The job array also leaves per-task files in `results/parts/` and logs in `results/logs/` — you
can ignore those; `merge_results.py` combines the parts into the same `tm_results.csv`.)

**View them on the cluster** without downloading:

```sh
cat results/tm_results.csv      # print the table to the terminal
column -s, -t results/tm_results.csv | less   # nicer aligned view (q to quit)
```

The plot is an image, so it is easiest to look at after copying it to your own computer.

**Copy the results down to your computer** (run this **on your own machine**, not on the cluster):

```sh
scp -r <your-id>@transfer.gbar.dtu.dk:./27666_Protein_Design/Day_1/results ./YourpathOnYourComputer
```

You now have the scored table and the bar chart locally.

> **Note — notebook output is elsewhere:** the locations above are for the **batch** paths
> (single job and array). If you ran the **notebook** instead, it saves `tm_results.csv` directly
> in `Day_1/` (not in `results/`) and shows the plot inline rather than saving a PNG.

## 9. Optional — build your own environment

If you would rather not use the shared environment, build your own once (it will be called
`tmenv`):

```sh
module load miniconda3
conda env create -f environment.yml
conda env list            # check that "tmenv" appears
```

Then in the submit script, comment out the two shared-environment lines and switch the activation
to your own:

```sh
# source /dtu/blackhole/00/c27666/miniforge3/etc/profile.d/conda.sh
# conda activate protein-design
module load miniconda3
conda activate tmenv
```

That is the only change needed. Build the environment once, then submit jobs as above.

## 10. Good to know

- **Login node vs interactive vs compute.** You log into a login node, type `linuxsh` to reach an
  interactive node for hands-on work, and `bsub` sends jobs to compute nodes for the heavy lifting.
- **CPU only.** TM-align does not use a GPU, so these jobs run on the `hpc` queue, not a GPU queue - please keep it so.
- **Outputs stay out of Git.** The `results/` folder and the generated CSV / PNG are ignored by
  `.gitignore`, so runs will not clutter the repository.
- **First-run check.** The first time, run the Step 3 activation by hand; if `import tmtools`
  prints `ok`, every later submission will work too.

> **If activation fails:** double-check the path `/dtu/blackhole/00/c27666/miniforge3` and the
> env name `protein-design` against the course materials.
---

## Important reminder — what Day 1 is teaching you (and how it carries to GPU work)

Day 1 exercise is a deliberately small, fast, CPU-only exercise — but the point isn't just the TM-align
result. It's to learn the HPC habits you'll rely on for the heavy GPU work later in the project.

**What to take away from Day 1:**

- **The submission cycle:** log in → `linuxsh` → activate the environment → `bsub < script.sh` →
  monitor with `bjobs` → collect results. 
  This loop is the same for every job you'll run, CPU or GPU.
- **Match the resource to the job.** TM-align is CPU-only, so it runs on the `hpc` queue. 
  Always ask "does this tool actually use a GPU?" before choosing a queue. Putting CPU work on a GPU
  wastes a scarce resource and doesn't run faster.
- **The array pattern (Path C)** is how you run the *same job over many inputs* — screening
  hundreds or thousands of structures, samples, or sequences. For 10 targets it's overkill (the
  single job is faster), so here it's a teaching example. Learn the pattern now, on a safe CPU
  task, so you can use it for real later.

**When you move on to the heavy GPU jobs (protein-design workloads):**

- **The GPU pool is small and shared.** Treat every slice of GPU as
  something your classmates are also waiting for.
- **One job, one GPU.** Request `#BSUB -gpu "num=1:mode=exclusive_process"`. A single heavy run
  already uses its slice fully — there's nothing to gain from grabbing more.
- **Don't aim job arrays at the GPU queue, and don't try to split one job across GPUs.** Arrays
  are the CPU scaling pattern you learned here; on the shared GPU pool an array can swallow every
  slice at once and block the whole class. If you have several GPU runs to do, submit them as
  separate normal jobs and let the scheduler queue them.
- **Right-size and release.** Don't request far more memory, cores, or walltime than the job needs,
  and exit idle interactive GPU sessions so the slice frees up for the next person.
- **Start from the provided submit scripts** for each exercise rather than writing GPU job scripts
  from scratch.

In short: Day 1 teaches the workflow and the judgment — *which queue, how much to request, when to
parallelize and when not to* — so that when you reach the GPU-heavy work, you use a genuinely
scarce shared resource well.
