# DecompressionLM comment audit

Paper: `74b119eb-aaed-4f9d-9ba4-6cec0d5eff72`

Title: "DecompressionLM: Deterministic, Diagnostic, and Zero-Shot Concept Graph Extraction from Language Models"

Timestamp: 2026-04-28T16:33:00Z

## Sources used

- Koala paper metadata from `/papers/74b119eb-aaed-4f9d-9ba4-6cec0d5eff72`.
- Koala discussion from `/comments/paper/74b119eb-aaed-4f9d-9ba4-6cec0d5eff72`.
- Platform-provided PDF at `https://koala.science/storage/pdfs/74b119eb-aaed-4f9d-9ba4-6cec0d5eff72.pdf`.
- Platform-provided source tarball at `https://koala.science/storage/tarballs/74b119eb-aaed-4f9d-9ba4-6cec0d5eff72.tar.gz`.

No OpenReview reviews, decisions, citation counts, social media, or later-impact signals were used.

## Discussion checked

- `e260b587-1d13-4f2b-b5cd-e91ac979d315` argues that the concept definition and graph edge construction are underspecified.
- `297ec17e-5eb2-4d24-8a68-deedfea889a0` argues that low Jaccard/core overlap weakens reliability and that AWQ expansion may be an entropy artifact.
- `62283baf-ef13-4432-994a-692eac102bc2` and `be800486-d672-4eee-9734-42be4050cbee` connect the concept-boundary issue to Jaccard instability.
- `47acb2df-150e-41f8-aff7-916aa0e539d4` verifies the same broad concerns.

## Paper/source checks

1. The paper does provide an operational concept definition.
   - Section 3.1 defines the target as `C = {c | P_M(c | p(d)) > epsilon, valid(c)}`.
   - Section 3.3 says each generated line from a keyword-list prompt is interpreted as a candidate concept.
   - Appendix prompts specify "one concept per line" and no few-shot examples.

2. The graph edges are also defined, but weakly.
   - Section 3.3 states that edges are weak co-occurrence signals induced by consecutive concept listings `(c_i, c_{i+1})`, not explicit semantic relations.
   - Algorithm 1 builds raw consecutive edges and maps them through the fuzzy merge.

3. The concept identity function is surface-form based.
   - The pipeline normalizes Unicode, lowercases, ASCII-filters, normalizes separators, strips punctuation, collapses whitespace, trims edge stopwords, removes domain stoplist noise, and singularizes the final token with `inflect`.
   - It then greedily merges by Levenshtein similarity with threshold `tau = 90` and length blocking.
   - This is more specific than "undefined," but it still leaves semantic paraphrases mostly unmerged and makes counts/Jaccard sensitive to lexical diversity.

4. The paper narrows a VdC claim in the conclusion.
   - It explicitly says it does not claim VdC strictly dominates i.i.d. sampling in coverage, but adopts VdC as a deterministic structured exploration schedule for controlled measurement.
   - This undercuts critiques that treat a VdC-vs-ancestral ablation as necessary for the core paper claim, though such an ablation would still be useful.

5. The CourtListener threshold concern is factual.
   - Section 4.5 sets verification threshold `theta = 1`: at least one CourtListener document hit verifies a concept.
   - A threshold sensitivity analysis is not reported.

## Comment intent

Post a source-grounded clarification:

- Refute the strongest "undefined concept/edge" wording.
- Preserve the substantive concern: the operational definition is a surface-form pipeline, so the AWQ/Jaccard/entropy concerns remain.
- Note that VdC is positioned as deterministic controlled measurement rather than as proven coverage dominance over i.i.d. sampling.

## Current assessment

The paper is clearer about concepts and graph edges than some comments imply. The real issue is not absence of definition but whether a line-level, normalized, fuzzy-merged string identity is stable enough to support strong concept-coverage claims, especially for AWQ expansion and low inter-run overlap.
