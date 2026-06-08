#!/bin/bash
# ============================================================
# ONE-TIME SETUP – only needed when cloning for the first time
# ============================================================

# 1. Clone the repo
git clone https://github.com/YOUR-USERNAME/binder-design-workflows.git
cd binder-design-workflows

# ============================================================
# ADDING A NEW NOTEBOOK (after each update from Google Drive)
# ============================================================

# Download the notebook from Google Drive (manually in browser)
# Then copy it into the notebooks/ folder and commit:

# git add notebooks/my_new_notebook.ipynb
# git commit -m "Add: short description of the notebook"
# git push

# ============================================================
# TIP: Strip outputs from notebooks before committing
# (saves space, avoids noisy diffs on output cells)
# ============================================================

# Option A: jupyter nbconvert (recommended)
# pip install jupyter nbconvert
# jupyter nbconvert --clear-output --inplace notebooks/*.ipynb

# Option B: nbstripout (runs automatically on every commit)
# pip install nbstripout
# nbstripout --install   # run once inside the repo

echo "Setup guide read ✓"
echo "Remember to replace 'YOUR-USERNAME' in README.md and this file with your GitHub username!"
