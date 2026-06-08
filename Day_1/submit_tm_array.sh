#!/bin/sh
### =====================================================================
### TM-align structural comparison - JOB ARRAY
### One array task per target (each runs tm_compare_array.py once).
### Submit from inside the Day_1 folder:   bsub < submit_tm_array.sh
### Then merge once all tasks finish:       python merge_results.py
###
### The range [1-10] matches the 10 .pdb files in data/target_vhh.
### If you change the target set, update it:
###   ls data/target_vhh/*.pdb | wc -l    -> N, then use [1-N]
### Array is overkill for 10 targets - it exists to teach the pattern
### and to scale to hundreds/thousands of structures.
### =====================================================================

### -- job name + array range (EDIT 10 if your target count changes) --
#BSUB -J tm_array[1-10]
### -- to cap concurrent tasks (be kind to other users) use e.g. [1-10]%5 --
#BSUB -q hpc
#BSUB -n 1
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=4GB]"
#BSUB -W 00:15
### -- %J = job-id, %I = array index --
#BSUB -o results/logs/tm_%J_%I.out
#BSUB -e results/logs/tm_%J_%I.err

mkdir -p results/logs results/parts

# --- environment ---------------------------------------------------------
# Shared course environment - no edit needed for course 27666.
source /dtu/blackhole/00/c27666/miniforge3/etc/profile.d/conda.sh
conda activate protein-design

# --- environment -if not using shared env ------------
#source ~/miniconda3/etc/profile.d/conda.sh
#conda activate tmenv

# --- run one target, selected by the array index -------------------------
python tm_compare_array.py \
    --ref-dir    data/input_vhh \
    --target-dir data/target_vhh \
    --out-dir    results/parts \
    --index      $LSB_JOBINDEX
