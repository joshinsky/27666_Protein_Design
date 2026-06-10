# Day 3 — Computational Protein Design

We will run this notebook in Google Colab, not on the HPC to skip waiting times in the LSF queueing system. 

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

## Link to weights and installs 
 Open this link: 
 
https://drive.google.com/drive/folders/16U53YKuuZ8vJpc-OGXyaVFXr2kk9lz52?usp=sharing


## How to get started:

1. Open the link provided above.
2. Make a short-cut to your Google drive (Press on the tile of the folder protein_design and select 'Organise' and 'Add short-cut' 
<img width="1013" height="664" alt="Screenshot 2026-06-10 at 12 10 07" src="https://github.com/user-attachments/assets/8139c2f8-43c5-42c1-9292-f40f186ee671" />
3. Place this short-cut directly into 'Mydrive' and press 'add'
<img width="650" height="538" alt="Screenshot 2026-06-10 at 12 15 46" src="https://github.com/user-attachments/assets/af3aa23a-0240-4e91-a1dd-58d4d7b8b1b7" />
4. Navigate to your own drive by clicking on 'Mydrive' in the list of options on the left
<img width="254" height="580" alt="Screenshot 2026-06-10 at 12 18 39" src="https://github.com/user-attachments/assets/3ebdbac8-a4b6-4978-8a06-ae2f3318feb4" />
5. Go into the newly linked protein_design folder in your drive and open the jupyter file.
6. Google provides free resources of computing. We will need a GPU for RFdiffusion3 and RosettaFold3, so let's change the runtime type: 

<img width="1486" height="533" alt="Screenshot 2026-06-10 at 12 22 13" src="https://github.com/user-attachments/assets/48cf34d4-3e20-456f-ab25-db0fe3383808" />

Here we select Python as language and a T4 GPU as the computing resource.

<img width="606" height="591" alt="Screenshot 2026-06-10 at 12 22 32" src="https://github.com/user-attachments/assets/92e362d1-c1ec-44c9-92f7-d2e2f598c0bd" />

Now we are good to start:

<img width="471" height="190" alt="Screenshot 2026-06-10 at 12 22 58" src="https://github.com/user-attachments/assets/2e363589-6126-43b3-a442-cce5bd00b1a0" />




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

---

## Running your own designs

### Binder design against a new target

**1. Prepare your target structure**

Download the PDB of your target protein and trim it to the relevant chains/region. Upload the file to your Drive at:
```
MyDrive/protein_design/inputs/<your_target>.pdb
```

**2. Set campaign parameters** (top of the notebook)

```python
student_name = 'your_name'      # your name — controls where outputs are saved
campaign     = 'MY_TARGET'      # descriptive name for this target
experiment   = 'exp_01'         # increment for each new attempt
```

**3. Configure RFD3** (RFD3 cell)

```python
input_pdb = f'{inputs_dir}/<your_target>.pdb'

# contig: binder length range + fixed target residue segments from your PDB
# e.g. design a 60-100 aa binder against chain B residues 10-80
contig = '60-100,/0,B10-80'
length = '270-380'   # total length = binder + target segments

# hotspots: atoms on the target to steer the binder toward
# find key interface residues in PyMOL or from literature
select_hotspots = {
    'B45': 'NE2',       # chain, residue number: atom name(s)
    'B62': 'CA',
}
```

> **Finding hotspots**: Open your target PDB in PyMOL and identify residues you want the binder to contact — e.g. a receptor binding site, an epitope, or a functional loop. Use `show sticks, resi 45+62` to inspect them.

**4. Update the RF3 template**

`inputs/rf3_template.json` specifies the fixed target chains for structure validation. Open the file and update the `path` field to point to your target CIF (generated after RFD3 runs) and adjust chain indices to match your system.

**5. Scale up** (optional)

```python
diffusion_batch_size = 5    # designs per batch
n_batches            = 10   # run 50 total designs
```

For a quick test keep `diffusion_batch_size=1, n_batches=2` (~10 min on T4). For a real campaign use 50–200 total designs.

---

### Enzyme design around a new theozyme

**1. Prepare your theozyme structure**

You need a PDB containing:
- The protein scaffold (or just the catalytic residues in their correct geometry)
- The small-molecule ligand as a HETATM record

Upload to Drive at:
```
MyDrive/protein_design/inputs/<your_enzyme>.pdb
```

**2. Set campaign parameters** (top of the notebook)

```python
student_name = 'your_name'
family       = 'hydrolases'        # enzyme family
target       = 'my_enzyme'         # your target name
campaign     = 'rd1'               # round 1; increment for redesigns
```

**3. Configure RFD3** (RFD3 cell)

```python
input_pdb    = f'{inputs_dir}/<your_enzyme>.pdb'
ligand_name  = 'LIG'   # must exactly match the residue name in your PDB (HETATM column 18-20)

# contig: free scaffold ranges interspersed with fixed catalytic residues
# e.g. fix residues A50, A120, A180 from the input PDB
contig = '30-50,A50-50,40-60,A120-120,30-50,A180-180,30-50'
length = '150-220'   # total designed residues (excluding ligand)

# Catalytic residues — MPNN will NOT redesign these
catres = ['A50', 'A120', 'A180']
```

> **Identifying catalytic residues**: Use literature or the RCSB page for your PDB to find the active-site residues. In PyMOL: `select catres, resi 50+120+180 and chain A` to verify their geometry.

> **Ligand name**: In PyMOL run `select lig, organic` then check the residue name in the sequence viewer, or open the PDB in a text editor and look for the `HETATM` lines — the residue name is in columns 18–20.

**4. Scale up** (optional)

Same as binder design — increase `diffusion_batch_size` and `n_batches` for a real campaign. Filter thresholds (`n_chainbreaks == 0`, clash checks) are applied automatically before MPNN.

---

### General tips

- **Name your campaigns clearly** — `student_name/campaign/experiment` maps directly to your output folder on Drive. Use descriptive names so results are easy to find later.
- **Start small** — run 2–4 designs first to confirm the pipeline completes without errors before scaling up.
- **Check RFD3 outputs before MPNN** — the notebook plots chain break and clash metrics after RFD3. If most structures fail, revisit your `contig` or `hotspots` before spending GPU time on sequence design.
- **RF3 quality thresholds** — aim for `plddt > 0.7` and interface PAE `< 10`. Designs below these thresholds are unlikely to fold or bind as intended.
