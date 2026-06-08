#!/bin/sh
### =====================================================================
### TM-align structural comparison - SINGLE JOB
### Runs tm_compare.py once; it loops over all targets internally.
### Submit from inside the Day_1 folder:   bsub < submit_tm.sh
### Recommended for the ~10 structures in this exercise.
### =====================================================================

### -- job name --
#BSUB -J tm_compare
### -- queue (CPU; TM-align does not use a GPU) --
#BSUB -q hpc
### -- number of cores (TM-align is single-threaded; 1 is enough) --
#BSUB -n 1
### -- keep the core on one host --
#BSUB -R "span[hosts=1]"
### -- memory per core --
#BSUB -R "rusage[mem=4GB]"
### -- wall-clock limit hh:mm (10 structures finish in seconds) --
#BSUB -W 00:30
### -- email at start (B) and end (N): uncomment and set your address --
##BSUB -u your_email@dtu.dk
##BSUB -B
##BSUB -N
### -- output / error files (%J = job-id) --
#BSUB -o tm_compare_%J.out
#BSUB -e tm_compare_%J.err

# --- environment ---------------------------------------------------------
# Shared course environment - no edit needed for course 27666.
source /dtu/blackhole/00/c27666/miniforge3/etc/profile.d/conda.sh
conda activate protein-design

# --- environment - if not using shared env ---------------------------------------------------------
# EDIT THIS to match how you load Python on the cluster. Either a conda env:
#source ~/miniconda3/etc/profile.d/conda.sh
#conda activate tmenv

# ...or a module + virtualenv, e.g.:
#   module load python3/3.11
#   source ~/tmenv/bin/activate

# --- run -----------------------------------------------------------------
python tm_compare.py \
    --ref-dir    data/input_vhh \
    --target-dir data/target_vhh \
    --out-dir    results
