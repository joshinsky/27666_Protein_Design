# 🧬 Binder Design Workflows (Google Colab)

A collection of Google Colab notebooks for computational protein binder design using **RFdiffusion** and **ProteinMPNN**. Built for internal team use.

---

## 📓 Notebooks

| Notebook | Description | Open in Colab |
|----------|-------------|---------------|
| `01_rfdiffusion_binder_design.ipynb` | Structure-based binder diffusion with RFdiffusion | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YOUR-USERNAME/binder-design-workflows/blob/main/notebooks/01_rfdiffusion_binder_design.ipynb) |
| `02_proteinmpnn_sequence_design.ipynb` | Sequence design on fixed backbone with ProteinMPNN | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YOUR-USERNAME/binder-design-workflows/blob/main/notebooks/02_proteinmpnn_sequence_design.ipynb) |
| `03_combined_pipeline.ipynb` | End-to-end: RFdiffusion → ProteinMPNN → scoring | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YOUR-USERNAME/binder-design-workflows/blob/main/notebooks/03_combined_pipeline.ipynb) |

> **Note:** Replace `YOUR-USERNAME` with your GitHub username for the Colab badges to work.

---

## 🔧 Prerequisites

- Google account (for Colab)
- Colab Pro recommended (A100 GPU for RFdiffusion)
- Input: target protein as a `.pdb` file

## 🚀 Quick Start

1. Click the **"Open in Colab"** badge for the desired notebook
2. Go to **Runtime → Change runtime type → GPU (A100)**
3. Run the setup cells (installs all dependencies automatically)
4. Upload your `.pdb` file or use the example data

---

## 🗂️ Workflow Overview

```
Target PDB
    │
    ▼
RFdiffusion          ← Generates backbone structures for the binder
    │
    ▼
ProteinMPNN          ← Designs sequences on the generated backbone
    │
    ▼
Scoring / Filtering  ← pAE, pLDDT, ipTM filtering
    │
    ▼
Top Candidates
```

---

## 📁 Repository Structure

```
binder-design-workflows/
├── README.md
├── notebooks/
│   ├── 01_rfdiffusion_binder_design.ipynb
│   ├── 02_proteinmpnn_sequence_design.ipynb
│   └── 03_combined_pipeline.ipynb
└── examples/
    └── example_target.pdb        ← Example input (optional)
```

---

## 📚 References

- [RFdiffusion (Watson et al., 2023)](https://www.nature.com/articles/s41586-023-06415-8)
- [ProteinMPNN (Dauparas et al., 2022)](https://www.science.org/doi/10.1126/science.add2187)

---

## 👥 Contact

For questions or issues: open a GitHub Issue or reach out in the team channel.
