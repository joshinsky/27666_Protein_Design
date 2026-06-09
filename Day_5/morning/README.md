# Day 5 — Morning session: Protein Language Models & AI applications in biology

**27666 · June 2026 (4 h · 09:00–13:00)**
**Lecturer**: Konstantinos Kalogeropoulos · DTU Bioengineering / Biosustain

This morning module pairs two short lectures with two hands-on Colab exercises.

| Block | Time | Content |
|---|---|---|
| Lecture 1 | 09:00 – 09:45 | Protein Language Models |
| Exercise 1 | 09:45 – 10:30 | `notebooks/01_plm_playground_*.ipynb` |
| Break | 10:30 – 10:45 | |
| Lecture 2 | 10:45 – 11:30 | AI applications in biology · foundation models · InstaNovo-FM |
| Exercise 2 | 11:30 – 12:30 | `notebooks/02_instanexus_nanobody_*.ipynb` |
| Wrap-up | 12:30 – 13:00 | Discussion · summary · bridge to the afternoon session |

---

## Learning objectives

By the end of the morning you will be able to:

- **Explain** what makes a "language model" suitable for protein sequences — and where the analogy breaks.
- **Describe** how a protein language model (pLM) is trained without labels, and what its embeddings encode.
- **Use** a pLM in the three canonical ways: frozen embeddings + linear probe, fine-tuning, and zero-shot scoring.
- **Recognise** the foundation-model paradigm in biology beyond protein sequence — single-cell, DNA, mass spectra.
- **Reason about** InstaNovo and InstaNovo-FM as foundation models for tandem mass spectrometry.
- **Inspect** raw InstaNovo predictions and **assemble** them into a full nanobody with InstaNexus.

---

## Notebooks

Each exercise has two notebook variants:

| File | Use |
|---|---|
| `*_solved.ipynb` | Reference. Has all the code filled in. Use for teaching or self-study. |
| `*_student.ipynb` | What you hand to students. Has **8 fill-in-the-blank `TODO_N` markers**. |

A small Python script (`make_student_notebooks.py`) regenerates the `_student` notebooks
from the `_solved` ones; the two cannot drift.

### Exercise 1 — pLM playground

Open in Colab: <https://colab.research.google.com/github/DigBioLab/27666_Protein_Design/blob/main/Day_5/morning/notebooks/01_plm_playground_student.ipynb>

- Load ESM-2 `t6_8M` (smallest ESM-2; runs on free Colab CPU)
- Embed 10 nanobodies + 10 human IGHV germlines + 10 shuffled controls
- PCA + UMAP visualisation → save a PNG suitable for slides
- 5-fold logistic-regression classifier on the embeddings
- Zero-shot mutational scan of nb6's CDR3 (preview of Exercise 2)
- **Downstream task**: predict enzyme optimal pH from sequence (composition baseline vs ESM-2 embeddings + Ridge)

### Exercise 2 — Inspect InstaNovo predictions & assemble nb6

Open in Colab: <https://colab.research.google.com/github/DigBioLab/27666_Protein_Design/blob/main/Day_5/morning/notebooks/02_instanexus_nanobody_student.ipynb>

- `wget` the nb6 InstaNovo predictions from `Day_5/morning/data/NB6.csv`
- **Pre-assembly checks**: per-residue confidence (0–1 scale), peptide length by protease, inter-protease Jaccard overlap, pre-assembly coverage of the reference
- Run `instanexus` in both **greedy** and **De Bruijn graph (k = 7)** modes
- Load the final consensus FASTAs from `outputs/nb6/<mode>_c0.8[_ks7]/scaffolds/consensus/consensus_fasta/`
- Pairwise-align scaffolds against the known nb6 reference → coverage plot with CDR1/2/3 highlighted
- (Stretch) re-embed the best scaffold with ESM-2 → cosine similarity to the reference → closes the loop with Exercise 1

---

## Data

| File | Source | Used by |
|---|---|---|
| `data/NB6.csv` | InstaNovo predictions on a single nanobody (nb6), 9 proteases, DTU Bioengineering Proteomics Core 2025 | Exercise 2 |

The metadata JSON + contaminants FASTA are generated **inline** by Notebook 2 (no upload needed).

---

## Slides

Slides for both lectures live in `slides/` and are produced from markdown outlines via
`build_pptx_v2.py` (in the parent course folder). Each `.pptx` carries:

- DTU-orange banner at the top of every content slide (matching course 27833 Day 3 style)
- Slide numbers (`N / total`)
- Real figures embedded from the Gurev MLCB 2024 deck (Module 1) and the author's
  foundation-model PNGs (Module 2)
- Citation footers naming the original source for every reused figure

---

## Setup

Free-tier Google Colab handles everything end-to-end. Only Notebook 2 needs a
real install:

```python
!pip install -q 'pandas==2.2.2' instanexus logomaker biopython matplotlib seaborn
!apt-get install -y -qq clustalo > /dev/null
# MMseqs2 static binary fetched from mmseqs.com
```

Restart the runtime after the `pip install` if `pandas` was already imported.

---

## Citations

- **InstaNovo** — Eloff K.\*, Kalogeropoulos K.\* et al. *Nat Mach Intell* 7, 565–579 (2025).
- **InstaNexus** — Reverenna M. et al. *Mol Cell Proteomics* 25:4 (2026).
- **InstaNovo-FM** — Nieuwoudt M., Reverenna M., …, Kalogeropoulos K. *in preparation*, 2026.
- **ESM-2** — Lin Z. et al. *Science* 379, 1123–1130 (2023).
- **MMseqs2** — Steinegger M., Söding J. *Nat Biotech* 35, 1026–1028 (2017).
- **Clustal Omega** — Sievers F. et al. *Mol Syst Biol* 7, 539 (2011).
- **phopt** pH-prediction dataset — distributed via the ESM2-Tutorial repo (Gado et al. 2024).
- Lecture 1 visuals — adapted from Sarah Gurev's MLCB 2024 PLM tutorial (with credit to Aaron Kollasch, Noor Youssef, John Ingraham, Adam Riesselman).
