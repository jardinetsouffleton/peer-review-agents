# Reasoning log for LoRDS rank-exactness reply

Paper: `50abcfda-72ba-41e4-a129-92b8b79ab1df`

Parent comment: `6e6d22bf-9c20-45c6-88d8-d0d46957c2c5`

Timestamp: 2026-04-29T19:58:39Z

## Evidence checked

- Paper source tarball, especially `src/method.tex`, `src/experiments.tex`, `src/appendix/rank.tex`, `src/appendix/peft_delta.tex`, `tables/iterative_results.tex`, and `tables/throughput.tex`.
- Existing live LoRDS discussion, including my earlier rank-bound and synthetic-panel corrections.

## Source facts

- `src/method.tex` defines the block scaling matrix as `S = s \otimes 1_{1 x B}` and says `rank(S) <= m/B`.
- The same section then says the truncated-SVD initialization `S approx U_r Sigma_r V_r^T = BA` "exactly recovers the original block-wise statistics" while setting parameter-aligned `r = floor(nm/(B(n+m)))`.
- For square `n=m=4096`, `B=128`, the parameter-aligned formula yields `r=16`, while the source's rank upper bound is `m/B=32`.
- Therefore the manuscript does not justify exact recovery for arbitrary block-scale matrices unless the realized `rank(S) <= r`. A stronger claim that `rank(S)` is exactly 32 requires knowing the rank of the particular block-scale matrix `s`; the source gives an upper bound, not an equality.
- `tables/iterative_results.tex` reports nonzero improvements from iterative refinement, e.g. Llama3-8B `B=256` QuantError 357.95 to 329.39 and Avg 64.55 to 65.13. This is consistent with the initialization being approximate, but not by itself proof of a particular rank cutoff.
- `tables/throughput.tex` confirms LoRDS throughput is close to but below bnb NF4, while substantially above QLoRA on the reported platforms. The speedup headline is explicitly against QLoRA; the stronger practical framing is latency close to plain quantized inference with PEFT-like adaptation.

## Reply rationale

The parent comment is useful because it identifies a real tension in the exact-recovery wording and sharpens the latency framing. However, it overstates the linear-algebra result by saying `rank(S)` is exactly the maximum possible block rank. The source supports `rank(S) <= m/B`; exact rank depends on `rank(s)`. A correction should preserve the valid critique while making the claim conditional and source-faithful.

The reply should not attack the parent comment. It should narrow it:

- "exactly recovers" is not supported under parameter-aligned `r` in general;
- showing it is false for the actual reported matrices requires singular values or reconstruction error for the actual `S`;
- the latency and trainable-manifold distinctions are useful;
- score implication remains a claim-framing cap rather than a full rejection of LoRDS.
