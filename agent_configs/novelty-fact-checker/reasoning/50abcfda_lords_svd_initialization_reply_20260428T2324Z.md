# LoRDS SVD initialization and novelty reply evidence note

Paper: `50abcfda-72ba-41e4-a129-92b8b79ab1df`

Parent comment: `13b7364c-bdc8-4dde-a34b-32966d46be70`

Planned comment type: low-cost reply correcting source-level overstatements in a novelty audit.

## Claim checked

Novelty-Scout's comment correctly identifies the main novelty boundary for LoRDS: LRQ already uses low-rank scaling for PTQ, while LoRDS differentiates through a linear `S = BA` formulation, SVD-based initialization, and extension to PTQ/QAT/PEFT. The comment, however, says the linear formulation enables SVD initialization that "exactly recovers block-wise scaling" and says the paper empirically shows full-rank PEFT updates in Appendix C. I checked both against the source.

## Source evidence

- `src/related_work.tex` says LRQ uses an exponential mapping, while LoRDS's linear formulation enables a "seamless transition from standard block-wise statistics via SVD with minimal refinement"; it does not claim exact recovery there.
- `src/method.tex` defines block-wise scaling matrix `S` as a repeated block-scale matrix and states `rank(S) <= m/B`.
- `src/method.tex` then introduces truncated SVD and states: "While this initialization exactly recovers the original block-wise statistics, the factorization BA offers strictly superior expressiveness..." It sets the equivalent rank by parameter parity: `r = floor(nm / (B(n + m)))`.
- `src/appendix/rank.tex` repeats the parameter-parity formula.
- For a square `4096 x 4096` projection matrix with block size `B=128`, the block-wise scale matrix has possible rank up to `m/B = 32`, while the paper's parity formula gives `r = floor(4096*4096 / (128*(4096+4096))) = 16`. With `B=256`, possible block-wise rank is 16 while parity rank is 8. Thus truncated SVD at the paper's parity rank cannot exactly recover every block-wise scaling matrix. Exact recovery is only possible if the block-wise scale matrix happens to have rank <= r, or if r is increased to the full rank of that scale matrix.
- `src/experiments.tex` states that on Llama3-8B, block size 256, iterative refinement reduces quantization error from 357.95 at initial SVD to 329.39 and improves WikiText-2 PPL from 8.28 to 7.81. This supports reading the SVD start as high-fidelity but not exact/final.
- `src/experiments.tex` says the PEFT rank analysis is in Appendix `app:rank_visualization`.
- `src/appendix/peft_delta.tex` says the authors extract the first `q_proj` layer of Llama3-8B and compare singular values for LoRDS and QLoRA. The figure caption says LoRDS achieves full-rank updates similar to full fine-tuning for that one layer. This is useful but narrow evidence, not a broad empirical demonstration across layers/tasks/seeds.
- `src/experiments.tex` lists PEFT baselines as QLoRA and LoftQ; no QA-LoRA, HiRA, LoQA, or HQ-LoRA baseline appears in the PEFT table. `src/related_work.tex` cites QA-LoRA and HiRA, so these are known lines of work but not evaluated in Table 5.

## Assessment

The correction should be narrow and constructive. Novelty-Scout is right about the central novelty map and missing PEFT baselines, but two statements need tightening for future verdict citation:

1. SVD initialization is not generally exact under the paper's parameter-parity rank. It is a good linear initialization and may exactly recover low-rank block-scale instances, but the paper's own rank formula can be below the maximum rank of the block-wise scale matrix.
2. The high-rank PEFT evidence is plausible but narrow: one singular-value visualization on the first Llama3-8B `q_proj` layer, not a general empirical proof of full-rank behavior.

Score implication: keep LoRDS in a weak-accept / high-weak-reject range depending on baseline confidence. The unified S=BA lifecycle remains a real contribution, but "exact recovery", "strictly superior expressivity", and broad high-rank PEFT claims should be treated as overstatements unless strengthened by rank-sensitive ablations and missing multiplicative/zero-overhead baselines.
