# Teaching Notes
**Author/contact:** Jonathan Funk ([jonfu@dtu.dk](mailto:jonfu@dtu.dk))

These notes summarize constructive improvements for the ML4Proteins exercises and can be used when preparing lectures, tutorials, or teaching-assistant guidance.

## What Works Well

- The course uses real protein datasets, which makes the exercises more meaningful than toy-only ML examples.
- The progression from sequence representation to model training, representation learning, and experiment selection is coherent.
- The notebooks expose enough code for students to see the workflow rather than treating ML as a black box.

## Main Teaching Gaps To Watch

- Many tasks originally asked students to implement a method but did not ask them to predict, interpret, or critique the result.
- Empty code cells can be intimidating for weaker students unless paired with explicit success criteria or hints.
- Model metrics need more biological framing. Students should repeatedly ask whether a metric would change an experimental decision.
- Representation learning can become abstract quickly. Keep returning to concrete questions: what information is preserved, what is discarded, and what similarity the model can now see.
- The notebooks should distinguish identifiers from measurements, especially for class labels and amino-acid encodings.

## Facilitation Pattern

Use this rhythm for most sections:

1. Ask students to make a prediction before running code.
2. Have them run or complete the code.
3. Ask them to explain the result to a neighbor without using package names.
4. Ask one pair to share a misconception or surprising result.
5. Only then discuss the formal concept.

## High-Value Questions

- What baseline would make this model look less impressive?
- What would data leakage look like in this dataset?
- Which representation assumptions are biological, and which are just computational convenience?
- If two models have similar scores, which one would you trust for selecting lab experiments, and why?
- What kind of experimental failure would this metric not reveal?
- What would you change if testing a variant cost 10 EUR, 100 EUR, or 1000 EUR?

## Suggested Extensions

- Add small instructor solution notebooks or hidden answer snippets for teaching assistants.
- Add short "debug this result" cells where students diagnose intentionally poor splits, class imbalance, or overfitting.
- Add a final mini-project where each group proposes 5-10 variants and defends the choice using model score, uncertainty, diversity, and feasibility.
- For advanced students, add scaffolded comparisons between OHE, BLOSUM, k-mer, and learned representations on the same train/test split.
