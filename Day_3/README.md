# Day 3 — Computational Protein Design

Two end-to-end design pipelines running on Google Colab: **binder design** (de novo protein binders against a target) and **enzyme design** (scaffolding a theozyme around a fixed catalytic geometry). Both follow the same three-step workflow:

```
RFdiffusion3 (RFD3)  →  ProteinMPNN / LigandMPNN  →  RosettaFold3 (RF3)
     backbone                  sequence                  structure validation
```

---

## Notebooks

| Notebook | Description |
|----------|-------------|
| `protein_design/binder_design_colab.ipynb` | Design de novo protein binders against a target structure. Hotspots and contigs define the interface; RFD3 generates backbones, MPNN designs sequences, RF3 validates the complex. |
| `protein_design/enzyme_design_colab.ipynb` | Scaffold a theozyme — catalytic residues and ligand geometry are fixed while RFD3 designs the surrounding protein. LigandMPNN designs sequences conditioned on the ligand; RF3 validates. |

---

## Folder structure

```
protein_design/
├── binder_design_colab.ipynb   # binder design pipeline
├── enzyme_design_colab.ipynb   # enzyme design pipeline
├── inputs/
│   ├── 5XH3.pdb                # serine hydrolase target (enzyme design)
│   ├── 6e3y_binding_site.pdb   # CLR/RAMP1 binding site (binder design)
│   ├── 6e3y_cut.pdb            # trimmed CLR/RAMP1 target
│   └── rf3_template.json       # RF3 input template (fixed target chains)
├── LigandMPNN/                 # LigandMPNN source (sequence design with ligand context)
├── support/
│   ├── rf3_metrics.py          # parse and filter RF3 output metrics
│   ├── rf3_metrics_foundry.py  # foundry-compatible variant
│   ├── cif_distance_analysis.py
│   └── jupyter_utils.py
└── runs/                       # pipeline outputs (per student / campaign / experiment)
```

---

## Setup

The notebooks run on **Google Colab** and read all inputs and model weights from **Google Drive**. No local installation is required.

**Required Drive folder structure** (one-time instructor setup):

```
MyDrive/protein_design/
├── models/
│   ├── rfd3_latest.ckpt                        # RFdiffusion3 backbone diffusion
│   ├── rf3_foundry_01_24_latest_remapped.ckpt  # RosettaFold3 structure prediction
│   ├── proteinmpnn_v_48_020.pt                 # ProteinMPNN sequence design
│   ├── ligandmpnn_v_32_010_25.pt               # LigandMPNN sequence design
│   └── rc_foundry-*.whl                        # rc-foundry Python package
```

> Model weights are **not stored in this repository** due to their size (5.4 GB). They must be present in the shared Drive folder before running the notebooks.

**To start a session:**
1. Open either notebook in Google Colab (Runtime → Python 3.12)
2. Run **Step 0** — mounts Drive, installs packages, clones LigandMPNN
3. Set `student_name` and campaign/experiment parameters
4. Run cells sequentially

---

## Pipeline steps

### 1. RFdiffusion3 (backbone generation)
Generates de novo protein backbone structures by diffusing from noise under structural constraints. For binder design, hotspot residues and a contig string guide the interface geometry. For enzyme design, catalytic residues are fixed in their theozyme geometry.

### 2. ProteinMPNN / LigandMPNN (sequence design)
Designs amino acid sequences onto the generated backbones. ProteinMPNN is used for binder design (redesigning the binder chain freely); LigandMPNN is used for enzyme design (conditioning on the small-molecule ligand). Structures with chain breaks or clashes are filtered before this step.

### 3. RosettaFold3 (structure validation)
Predicts the full complex structure for each designed sequence. Key quality metrics:
- `plddt` / `best_binder_plddt` — model confidence (aim > 0.7)
- `ptm` — predicted TM-score (higher is better)
- `AF_best_min_pae` / `AG_best_min_pae` — interface PAE (lower is better)
- `ipsae_interface` — interface-specific PAE

Outputs are written to `runs/<student_name>/<campaign>/<experiment>/`.
