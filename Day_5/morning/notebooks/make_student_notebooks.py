#!/usr/bin/env python3
"""Generate `*_student.ipynb` from `*_solved.ipynb` for both exercise notebooks.

Each blank is an exact-string find/replace against the solved source. The student
notebook also gets an orientation markdown at the top listing every blank.

Re-run after any edit to a solved notebook:

    python3 make_student_notebooks.py
"""
import copy
import json
import re
from pathlib import Path

HERE = Path(__file__).parent


# ─── shared helpers ───────────────────────────────────────────────────────────
def student_intro_md(blanks) -> dict:
    lines = [
        '## 🧑‍🎓 Student notebook — fill in the blanks!\n',
        '\n',
        f'This notebook contains **{len(blanks)} `TODO_N` markers** where you need to write a '
        'small piece of code before the cell will run. Each `TODO` is a real design choice '
        'a researcher makes — not a trick. If you get stuck, the markdown above the cell and '
        'the hint in the comment usually contain the answer.\n',
        '\n',
        '**The blanks**:\n',
        '\n',
    ]
    for _, _, hint in blanks:
        lines.append(f'- {hint}\n')
    lines += [
        '\n',
        'Cells run top-to-bottom. If a cell crashes with `SyntaxError` or `NameError`, '
        'check for an unfilled `____` or `___`. A `_solved` companion notebook exists '
        '— try to resist looking at it!\n',
    ]
    return {
        'cell_type': 'markdown',
        'id': 'student-intro',
        'metadata': {},
        'source': lines,
    }


def derive_student(solved_path: Path, student_path: Path, blanks):
    nb = json.loads(solved_path.read_text())
    nb = copy.deepcopy(nb)

    applied = {i + 1: False for i in range(len(blanks))}
    for cell in nb['cells']:
        if cell['cell_type'] != 'code':
            continue
        src = cell['source']
        is_list = isinstance(src, list)
        text = ''.join(src) if is_list else src
        for i, (find, repl, _) in enumerate(blanks):
            if find in text:
                text = text.replace(find, repl)
                applied[i + 1] = True
        cell['source'] = text.splitlines(keepends=True)
        cell['outputs'] = []
        cell['execution_count'] = None

    missed = [i for i, ok in applied.items() if not ok]
    if missed:
        raise SystemExit(
            f'! In {solved_path.name}, these TODO blanks could not be matched: {missed}'
        )

    # Insert orientation markdown right after the title
    nb['cells'].insert(1, student_intro_md(blanks))

    student_path.write_text(json.dumps(nb, indent=1, ensure_ascii=False))
    print(f'✓ {student_path.name}: {len(nb["cells"])} cells, {len(blanks)} blanks applied.')


# ============================================================================
# Notebook 1 — pLM playground
# ============================================================================
NOTEBOOK1_BLANKS = [
    (
        'return hidden.mean(dim=0).cpu().numpy()',
        'return hidden.____(dim=0).cpu().numpy()    # TODO_1: which reduction collapses '
        '(seq_len, hidden) → (hidden,)? options: mean / sum / max / min — explain your choice.',
        '`TODO_1` (Sec. 4) — choice of pooling reduction in `embed_sequence`.',
    ),
    (
        'hidden = out.last_hidden_state[0, 1:-1]  # drop BOS, EOS',
        'hidden = out.last_hidden_state[0, _:_]    # TODO_2: ESM tokenises as '
        '[BOS] r1 r2 ... rL [EOS] — slice out the residues only (Python slice notation).',
        '`TODO_2` (Sec. 4) — slice to drop BOS and EOS tokens.',
    ),
    (
        'reducer = umap.UMAP(n_components=2, random_state=RNG_SEED, n_neighbors=8, min_dist=0.3)',
        'reducer = umap.UMAP(n_components=2, random_state=RNG_SEED, n_neighbors=___, min_dist=0.3)'
        '    # TODO_3: UMAP local neighbourhood size — small (~5) emphasises local clusters; '
        'large (~30) emphasises global structure. Pick a value for ~30 sequences.',
        '`TODO_3` (Sec. 5) — UMAP `n_neighbors`.',
    ),
    (
        'cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RNG_SEED)',
        'cv = StratifiedKFold(n_splits=___, shuffle=True, random_state=RNG_SEED)'
        '    # TODO_4: number of cross-validation folds — with 10 examples per class, '
        'how many folds keep at least one example of each class per fold?',
        '`TODO_4` (Sec. 6) — number of CV folds.',
    ),
    (
        'MAX_LEN = 400      # TODO_5: cap sequence length to keep embedding fast on free Colab CPU (try 400)',
        'MAX_LEN = ____     # TODO_5: cap sequence length to keep embedding fast on free Colab CPU. '
        'Trade-off: shorter = faster, but you discard real enzymes. Try 400 first.',
        '`TODO_5` (Sec. 8) — maximum sequence length to embed.',
    ),
    (
        'N_TRAIN = 300      # TODO_6: how many training sequences to embed? (try 300 — ~4-5 min on CPU)',
        'N_TRAIN = ____     # TODO_6: how many training sequences to embed? '
        'More = better model, but slower. ~300 takes 4-5 min on CPU. ~50 is fast but poor.',
        '`TODO_6` (Sec. 8) — number of training sequences to embed.',
    ),
    (
        'return np.array([seq.count(aa) / L for aa in AA_VOCAB])    # TODO_7: fill in the composition formula',
        'return np.array([___ for aa in AA_VOCAB])    # TODO_7: for each amino acid `aa` in '
        'AA_VOCAB, return its fractional occurrence in `seq` (count divided by length L).',
        '`TODO_7` (Sec. 8) — amino-acid composition formula.',
    ),
    (
        'RIDGE_ALPHA = 1.0    # TODO_8: regularisation strength (try 1.0 first; 0.1 and 10.0 are also reasonable)',
        'RIDGE_ALPHA = ___    # TODO_8: Ridge regularisation strength. '
        'Small α = closer to ordinary least squares; large α = stronger shrinkage toward zero. Try 1.0.',
        '`TODO_8` (Sec. 8) — Ridge regularisation strength α.',
    ),
]


# ============================================================================
# Notebook 2 — InstaNexus on nb6
# ============================================================================
NOTEBOOK2_BLANKS = [
    # TODO_1: --conf cutoff (appears in both greedy + dbg commands; one replace catches both)
    (
        "'--conf', '0.8',",
        "'--conf', '___',    # TODO_1: InstaNovo confidence cutoff. The InstaNexus README "
        "uses 0.9 for BSA (~600 aa, high redundancy). nb6 is ~150 aa — should you be stricter "
        "or more permissive? (try 0.8)",
        '`TODO_1` (Sec. 5+6) — InstaNovo confidence cutoff `--conf` (applied to both greedy + DBG runs).',
    ),
    # TODO_2: --min-overlap
    (
        "'--min-overlap', '3',",
        "'--min-overlap', '_',    # TODO_2: minimum amino-acid overlap to chain two peptides "
        "in greedy mode. Trade-off: 2 → many false joins; 5 → very few chains. Try 3.",
        '`TODO_2` (Sec. 5+6) — minimum peptide overlap `--min-overlap`.',
    ),
    # TODO_3: --size-threshold (both modes)
    (
        "'--size-threshold', '8',",
        "'--size-threshold', '_',    # TODO_3: minimum number of peptides supporting a contig. "
        "BSA default is 12; for a 150-aa nanobody with limited redundancy, try 8.",
        '`TODO_3` (Sec. 5+6) — minimum peptides supporting a contig `--size-threshold`.',
    ),
    # TODO_4: --kmer-size (DBG only)
    (
        "'--kmer-size', '7',",
        "'--kmer-size', '_',    # TODO_4: De Bruijn k-mer length. Short k (3-5) = "
        "sensitive but more ambiguous walks; long k (9-11) = stricter but sparser graph. Try 7.",
        '`TODO_4` (Sec. 6) — DBG k-mer length `--kmer-size`.',
    ),
    # TODO_5: CDR1 boundaries
    (
        'CDR1 = (25, 35)',
        'CDR1 = (__, __)    # TODO_5: CDR1 of a VHH framework starts around position 25 '
        'and ends around position 35 (Kabat-ish numbering). Fill the boundaries.',
        '`TODO_5` (Sec. 8) — CDR1 boundary positions in the nb6 reference.',
    ),
    # TODO_6: CDR3 start  (connects to nb6 zero-shot scan in Notebook 1)
    (
        'CDR3 = (95, WGQ if WGQ > 0 else 115)',
        'CDR3 = (__, WGQ if WGQ > 0 else ___)    # TODO_6: CDR3 begins right after the canonical '
        'C-anchor (second Cys ~ position 95) and ends just before the WGQGTQ motif. Fill in '
        'both numbers — the second one is a fallback length used if WGQGTQ is not found.',
        '`TODO_6` (Sec. 8) — CDR3 start position and fallback end position.',
    ),
    # TODO_7: gap penalties in pairwise alignment
    (
        'aln = pairwise2.align.localxs(target, query, -2, -1, one_alignment_only=True)',
        'aln = pairwise2.align.localxs(target, query, ___, ___, one_alignment_only=True)'
        '    # TODO_7: gap-open and gap-extend penalties (both negative — they '
        'penalise gaps). -2 and -1 are reasonable defaults; make them more negative '
        'to discourage gaps further.',
        '`TODO_7` (Sec. 8) — gap-open and gap-extend penalties for scaffold→reference alignment.',
    ),
    # TODO_8: L2 normalization for cosine similarity
    (
        'return h / np.linalg.norm(h)',
        'return h / ___    # TODO_8: to make a dot product equal cosine similarity, '
        'normalise the vector by its L2 norm. Use `np.linalg.norm(h)`.',
        '`TODO_8` (Sec. 10) — L2 normalisation step that turns dot product into cosine similarity.',
    ),
]


def main():
    derive_student(HERE / '01_plm_playground_solved.ipynb',
                    HERE / '01_plm_playground_student.ipynb',
                    NOTEBOOK1_BLANKS)
    derive_student(HERE / '02_instanexus_nanobody_solved.ipynb',
                    HERE / '02_instanexus_nanobody_student.ipynb',
                    NOTEBOOK2_BLANKS)


if __name__ == '__main__':
    main()
