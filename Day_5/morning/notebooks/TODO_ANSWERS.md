# Answer key for the `TODO_N` blanks

Walk-through of all 16 fill-in-the-blank markers across both student notebooks. Each entry shows the blank in context, the correct answer, and the reasoning a student should be able to articulate after the exercise.

Use this document either as a **lecturer cheat-sheet** during the session, or hand it out **after the exercise** as a debrief — but not during, otherwise students stop thinking.

---

## Exercise 1 — `01_plm_playground_student.ipynb`

### TODO_1 — slicing out residue tokens

```python
hidden = out.last_hidden_state[0, _:_]
```

**Answer**: `[0, 1:-1]`

**Reasoning**: ESM-2 (like BERT) tokenises a protein as
`[BOS] r₁ r₂ … r_L [EOS]`. The output `last_hidden_state` therefore has shape `(1, L+2, hidden_dim)`. The first index is the batch dimension (we have one sequence — index `0`). On the sequence axis we want only the **residue** tokens, so we drop the first (BOS) and last (EOS) positions with `1:-1`.

> Why it matters: if you forget to drop BOS/EOS your mean-pool averages in two **special** tokens whose embeddings are not residue-like — your downstream classifier accuracy quietly drops.

---

### TODO_2 — pooling over residues

```python
return hidden.____(dim=0).cpu().numpy()
```

**Answer**: `mean`

**Reasoning**: We start with a `(L, hidden_dim)` tensor and want a fixed `(hidden_dim,)` vector per protein. The four options collapse the seq-length axis differently:

| Op | What it does | When it makes sense |
|---|---|---|
| **mean** ✓ | Average over positions | **Default**: weighs every residue equally, works for almost any task |
| `sum` | Sum of embeddings | Mixes scale with length — longer proteins get bigger vectors |
| `max` | Per-dim maximum | Captures "the most extreme signal anywhere in the sequence" — useful for motif tasks |
| `min` | Per-dim minimum | Mirror of max; rarely useful |

> Mean is the standard. Max-pool sometimes helps for short-motif tasks (cleavage sites, signal peptides). Try the others at home and watch the classifier.

---

### TODO_3 — UMAP `n_neighbors`

```python
reducer = umap.UMAP(..., n_neighbors=___, min_dist=0.3)
```

**Answer**: `8` (anything in 5–10 is fine for 30 sequences)

**Reasoning**: `n_neighbors` is the size of the local neighbourhood UMAP balances local-vs-global structure against. With only **30 points** we cannot ask UMAP to look at 30 neighbours — that flattens everything into one blob. With 2 neighbours it over-fragments. 5–10 is the sweet spot for a tiny dataset.

> Rule of thumb: `n_neighbors ≈ √N` is a reasonable starting point; for big embedding sets you go to 30–50.

---

### TODO_4 — number of CV folds

```python
cv = StratifiedKFold(n_splits=___, shuffle=True, random_state=RNG_SEED)
```

**Answer**: `5`

**Reasoning**: We have 30 examples split into 3 classes of 10. `StratifiedKFold` keeps the class ratio constant per fold. The largest k that still puts at least one of each class in every fold is `10` (1 per class per fold), but with so few examples per fold the variance becomes silly. `5` gives 6 examples per fold (2 per class) — enough for the test fold to be meaningful, and we still train on 80% of the data each round.

> If anyone tries `n_splits=10` it works numerically but each fold has only 3 test examples; one mis-classification swings accuracy by 33%.

---

### TODO_5 — `MAX_LEN` (sequence-length cap for pH dataset)

```python
MAX_LEN = ____
```

**Answer**: `400`

**Reasoning**: ESM-2 attention is O(L²) in sequence length. On free Colab CPU, a 1000-residue protein takes ~5 seconds per forward pass; a 200-residue protein takes ~0.5 s. Capping at **400** retains ~75% of the dataset (enzymes are typically 200–500 aa) while keeping per-sequence inference under 1 s.

> Trade-off: lower cap = faster but you throw away real data; higher cap = slower and the laptop fan complains. There is no right answer — but values below 200 or above 800 are wrong.

---

### TODO_6 — `N_TRAIN` (training subsample size)

```python
N_TRAIN = ____
```

**Answer**: `300`

**Reasoning**: We are not trying to win a benchmark — we are showing that ESM-2 embeddings beat a composition baseline at a real task in 4–5 min of CPU time. 300 sequences gives Ridge enough signal to converge, and at ~1 s per embedding the slow cell runs in ~5 min on free Colab. With 50 sequences you cannot beat noise; with 1000 you wait 17 minutes.

> Push to 600 or 1000 at home and watch R² climb.

---

### TODO_7 — amino-acid composition formula

```python
return np.array([___ for aa in AA_VOCAB])
```

**Answer**: `seq.count(aa) / L`

**Reasoning**: The composition feature is the fraction of each of the 20 amino acids in the sequence. `seq.count(aa)` returns the raw count of `aa` in `seq`; dividing by length normalises so a 100-aa and a 600-aa protein produce comparable vectors.

> Forgetting the `/ L` makes the feature monotonic with length — your model then learns to predict from length, not from composition. Easy to fall into.

---

### TODO_8 — Ridge regularisation strength

```python
RIDGE_ALPHA = ___
```

**Answer**: `1.0`

**Reasoning**: Ridge adds `α · ‖β‖²` to the OLS loss. Small `α` → close to OLS (fits training noise); large `α` → coefficients shrink toward zero (under-fit). With ~300 examples and a 320-dim feature vector (more features than examples — the over-determined regime), regularisation matters. `α = 1.0` is the sklearn default and usually a sane start.

> Try `α ∈ {0.01, 0.1, 1, 10, 100}` and plot test R² — you should see the classic U-curve. `RidgeCV` does this automatically; the "things to try" cell at the end suggests it.

---

## Exercise 2 — `02_instanexus_nanobody_student.ipynb`

### TODO_1 — sort order in `remove_substring_contigs`

```python
contigs = sorted(set(contigs), key=len, reverse=____)
```

**Answer**: `True` (descending — longest first)

**Reasoning**: `remove_substring_contigs` iterates over `contigs` and keeps each only if it is **not** a substring of one we have already kept. For this rule to drop the right contigs (the short ones contained inside long ones), the long ones must be seen **first**. Hence `reverse=True`.

> If a student writes `reverse=False`, all the SHORT contigs are kept and the long ones are then dropped because they contain something already in `keep` — exactly the wrong outcome. Best illustrated by running both and printing `len(contigs)`.

---

### TODO_2 — confidence cutoff `CONF_CUTOFF`

```python
CONF_CUTOFF    = ___
```

**Answer**: `0.8`

**Reasoning**: We computed per-residue confidence as `exp(log_prob / L)` — a geometric mean of per-position probabilities on a 0–1 scale. The histogram earlier in the notebook (Section 4) showed most confident peptides clumping at 0.9+, with a long tail down to ~0.5. A cutoff of **0.8** keeps ~75% of confident peptides while removing the noisiest predictions. The InstaNexus README uses 0.9 — but that was tuned for BSA which has *much* more peptide redundancy than a 150-aa nanobody.

> Strict (0.9) → cleaner peptides but coverage gaps. Loose (0.7) → more peptides chained but more wrong joins. 0.8 is a good middle ground for nanobodies.

---

### TODO_3 — `MIN_OVERLAP`

```python
MIN_OVERLAP    = _
```

**Answer**: `3`

**Reasoning**: Two peptides chain only if a suffix of one exactly matches a prefix of the other for at least `MIN_OVERLAP` residues. At 20 amino acids, **3 random residues match by chance ≈ 1/8000** — rare but not impossibly so. Going below 3 produces many spurious joins (`AAA` matches anywhere). Going to 5 demands very specific overlaps; with sparse coverage you end up with very short contigs.

> The InstaNexus paper uses 3 for nanobodies and antibodies. It's a sensible default.

---

### TODO_4 — `SIZE_THRESHOLD`

```python
SIZE_THRESHOLD = _
```

**Answer**: `8`

**Reasoning**: After per-protease assembly we want to drop contigs that are "too short to be evidence" before scaffolding across proteases. A contig of 4 residues is just a tetra-peptide — could be noise. A contig of 8+ residues is much more likely to be a real region of the protein. For a 150-aa nanobody, **8** is the InstaNexus paper's recommended value.

> Going to 12 (BSA default) discards a lot of legitimate short evidence in the CDR regions. Going to 4 floods the scaffolding stage with noise.

---

### TODO_5 — CDR1 boundaries

```python
CDR1 = (__, __)
```

**Answer**: `(25, 35)`

**Reasoning**: VHH (nanobody) CDR1 lies between framework regions FR1 and FR2 in the immunoglobulin variable domain. Using **Kabat-ish numbering** applied to the nb6 sequence:
- FR1 ends around residue 24 (`SCTAS` motif).
- CDR1 spans roughly residues **25–35** (`LNIFSINAMG` in nb6).
- FR2 starts at residue 36 (`WYRQ`).

These are approximate — for production work students would use **ANARCI** or **IMGT** numbering, which align by structural position rather than raw index. The notebook explicitly says "approximate" so students know what they are doing.

---

### TODO_6 — CDR3 start + fallback end

```python
CDR3 = (__, WGQ if WGQ > 0 else ___)
```

**Answer**: `(95, ..., 115)`

**Reasoning**:
- **CDR3 starts** at the second canonical Cys (~position 95 in Kabat). In nb6 this is the `C` of `…YYC HAEGPFNIATKEQYDY…` — exactly position 95.
- **CDR3 ends** just before the `WGQGTQ` motif (start of FR4). The code first searches for that motif (`WGQ = NB_REF.find('WGQGTQ')`) and uses its index if found. The fallback `115` is the typical position if the motif is absent — useful when the WGQGTQ is mutated or the sequence is truncated.

This is the **most pedagogically rich blank** because Notebook 1's bonus cell scans this exact region for residue preferences in nb6. The two notebooks share a hidden link through this blank.

---

### TODO_7 — gap penalties in local alignment

```python
aln = pairwise2.align.localxs(NB_REF, q, ___, ___, one_alignment_only=True)
```

**Answer**: `-2, -1`

**Reasoning**: `pairwise2.align.localxs(target, query, gap_open, gap_extend, ...)`. Both penalties are **negative** because they subtract from the alignment score.
- **Gap open = −2**: opening a new gap costs 2 points.
- **Gap extend = −1**: each additional residue in the gap costs 1 more point.

The asymmetry (open > extend) is biologically motivated — one long gap is more plausible than many short scattered gaps. With perfect matches scoring +1 (the default `x` parameters), `(−2, −1)` is a balanced choice for amino-acid alignments of ~100-residue sequences.

> Stricter penalties like `(-5, -3)` force tighter alignments and may miss real but slightly mis-aligned peptides. Looser penalties like `(-1, -0.5)` accept too many gappy alignments and the coverage plot becomes a mess.

---

### TODO_8 — L2 normalisation for cosine similarity

```python
return h / ___
```

**Answer**: `np.linalg.norm(h)`

**Reasoning**: Cosine similarity is defined as `cos(a, b) = (a·b) / (‖a‖ · ‖b‖)`. If we pre-normalise each vector to unit length by dividing by its L2 norm (`np.linalg.norm`), then **the dot product alone equals the cosine similarity**:

```
(a / ‖a‖) · (b / ‖b‖) = (a · b) / (‖a‖ · ‖b‖) = cos(a, b)
```

In the ESM-closure cell at the end of Notebook 2, this is why we compute `ref_emb @ scaf_emb` (a single dot product) and call it the cosine similarity — both vectors were pre-normalised inside `embed()`. If a student forgets the `/ np.linalg.norm(h)`, the printed "cosine similarity" can come out to values like 35 or 200 — clearly not a similarity.

> Beautiful little linear-algebra moment that ties back to *every* embedding-comparison task in machine learning.

---

## Summary table

| Notebook | Blank | What it controls | Answer | Why |
|---|---|---|---|---|
| 1 | TODO_1 | BOS/EOS slice | `1:-1` | ESM tokenises as `[BOS] r₁ … r_L [EOS]` |
| 1 | TODO_2 | Pooling | `mean` | Length-invariant, default |
| 1 | TODO_3 | UMAP `n_neighbors` | `8` | Small dataset → small neighbourhood |
| 1 | TODO_4 | CV folds | `5` | 10/class → 5-fold keeps 2/class per test fold |
| 1 | TODO_5 | `MAX_LEN` | `400` | O(L²) attention; 75% of enzymes survive |
| 1 | TODO_6 | `N_TRAIN` | `300` | ~5 min on CPU, enough signal for Ridge |
| 1 | TODO_7 | AA composition | `seq.count(aa) / L` | Length-normalised |
| 1 | TODO_8 | Ridge α | `1.0` | sklearn default; sane for `p ≫ n` |
| 2 | TODO_1 | Substring sort | `True` | Longest first ⇒ correct substring rule |
| 2 | TODO_2 | `CONF_CUTOFF` | `0.8` | Balances signal vs noise for ~150-aa target |
| 2 | TODO_3 | `MIN_OVERLAP` | `3` | 3 random residues match ≈ 1/8000 |
| 2 | TODO_4 | `SIZE_THRESHOLD` | `8` | Small protein, lower than BSA's 12 |
| 2 | TODO_5 | CDR1 | `(25, 35)` | Kabat-ish numbering |
| 2 | TODO_6 | CDR3 | `(95, …, 115)` | Second Cys → WGQGTQ |
| 2 | TODO_7 | Gap penalties | `-2, -1` | Open > extend; balanced for AA alignment |
| 2 | TODO_8 | L2 norm | `np.linalg.norm(h)` | Unit vectors ⇒ dot product = cosine |
