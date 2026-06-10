# Day 5 (morning) — Protein Language Models & AI applications in biology

**27666 · June 2026 · Friday morning, 4 hours**

Welcome! This morning is split into two short lectures and two hands-on Colab exercises.

| Block | Time | Content |
|---|---|---|
| Lecture 1 | 09:00 – 09:45 | Protein Language Models |
| Exercise 1 | 09:45 – 10:30 | `notebooks/01_plm_playground_student.ipynb` |
| Break | 10:30 – 10:45 | ☕ |
| Lecture 2 | 10:45 – 11:30 | AI applications in biology · foundation models · InstaNovo-FM |
| Exercise 2 | 11:30 – 12:30 | `notebooks/02_instanexus_nanobody_student.ipynb` |
| Wrap-up | 12:30 – 13:00 | Group discussion |

---

## What you'll do today

By the end of this session you will have:

- Loaded the **ESM-2** protein language model in Colab and used it to embed sequences.
- Seen pLM embeddings cluster nanobodies, human heavy-chain antibodies and shuffled controls — and trained a small classifier on top.
- Used ESM-2 in **zero-shot mode** to score amino-acid preferences across a nanobody CDR3.
- Predicted the optimal pH of enzymes from sequence with ESM-2 embeddings + Ridge regression, and compared against a hand-crafted baseline.
- Inspected raw **InstaNovo** de novo peptide-sequencing predictions on a real nanobody MS dataset, with per-residue confidence scoring and protease-overlap diagnostics.
- Implemented and run a **greedy assembly algorithm** to reconstruct the full nanobody (nb6) from those peptides.
- Compared your assembly to the known reference and closed the loop by re-embedding it with ESM-2.

---

## Open the exercises in Colab

You don't need to clone anything — just click the badges below. Each notebook downloads its own data via `wget`.

### Exercise 1 — pLM playground

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DigBioLab/27666_Protein_Design/blob/main/Day_5/morning/notebooks/01_plm_playground_student.ipynb)

### Exercise 2 — Inspect InstaNovo predictions & assemble nb6

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DigBioLab/27666_Protein_Design/blob/main/Day_5/morning/notebooks/02_instanexus_nanobody_student.ipynb)

> If a notebook has trouble loading on Colab, save it to your Drive: *File → Save a copy in Drive*. Restart the runtime (`Runtime → Restart session`) after any `pip install` cell.

---

## How the notebooks are set up

Each exercise contains **8 fill-in-the-blank `TODO_N` markers**. Each blank is a real design choice a researcher makes — not a trick question. The markdown above the cell, and the hint inside the comment, usually contain the answer. The first markdown cell of each notebook lists every blank with the section it lives in, so you can use it as a checklist.

If a cell crashes with `SyntaxError` or `NameError`, double-check that every `___` and `____` placeholder has been filled in.

A `*_solved.ipynb` companion notebook exists in the same folder. Try to resist looking at it!

---

## Quick environment notes

Both notebooks run end-to-end on **free-tier Google Colab CPU** in about 5–15 minutes each. A GPU is faster for Exercise 1 (especially the pH-prediction section) but is not required.

- Exercise 1 installs only `transformers`, `umap-learn`, and the standard ML stack (~30 s).
- Exercise 2 installs only `biopython` plus the standard ML stack — no native binaries.

You will see one explicit `wget` cell in Exercise 2 that pulls `NB6.csv` (~10 MB) from this repository.

---

## Data

| File | Description |
|---|---|
| `data/NB6.csv` | InstaNovo de novo peptide predictions for nanobody **nb6**, digested with 9 different proteases, measured by LC-MS/MS at the DTU Bioengineering Proteomics Core Facility (2025). |

---

## Slides

Lecture slides will be uploaded to this folder separately and made available on DTU Learn.

---

## Going further

If you finish early or want to keep exploring pLMs on your own time, take a look at the **[Multiomics Analytics Group's `course_protein_language_modeling`](https://github.com/Multiomics-Analytics-Group/course_protein_language_modeling/tree/main)**. It is a fuller short-course on pLMs by Alberto Santos and colleagues at DTU Biosustain, with hands-on Colab notebooks that go beyond what we cover today — full-stack fine-tuning of ESM on a downstream task, per-residue embeddings, the `bio-embeddings` library, and *de novo* protein design with a pLM.

---

## Acknowledgements

Many figures in Lecture 1 are adapted from Sarah Gurev's protein language models tutorial at MLCB 2024 (with credit to Aaron Kollasch, Noor Youssef, John Ingraham, and Adam Riesselman). The enzyme optimal-pH dataset is distributed via the [ESM2-Tutorial](https://github.com/ProteinVision/ESM2-Tutorial) repository.

**Tools and papers**:

- **ESM-2** — Lin Z. et al. *Science* 379, 1123–1130 (2023).
- **InstaNovo** — Eloff K.*, Kalogeropoulos K.* et al. *Nat Mach Intell* 7, 565–579 (2025).
- **InstaNexus** — Reverenna M. et al. *Mol Cell Proteomics* 25:4 (2026).
- **InstaNovo-FM** — Nieuwoudt M., Reverenna M., …, Kalogeropoulos K. *in preparation*, 2026.

---

**Course lecturer (morning session)**: Konstantinos Kalogeropoulos · DTU Bioengineering / Biosustain
