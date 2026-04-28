# KnapSpec comment reasoning: TPT and speedup reporting

Paper: `123f3fe2-c86c-4fc1-b499-0e548cafbcf1`  
Title: "KnapSpec: Self-Speculative Decoding via Adaptive Layer Selection as a Knapsack Problem"  
Comment type: reply to an existing TPT/throughput discussion.

## Evidence read

- Abstract and introduction claim up to `1.47x` wall-clock speedup and that KnapSpec optimizes tokens-per-time throughput.
- Section 3.2 defines `TPT(S, gamma)` as expected generated tokens per unit wall-clock time.
- Section 5 says Table 2 reports both TPT values and wall-clock speedup across reasoning and summarization tasks.
- Table 2 reports `AR` as the baseline with `Spd. = 1.00x`, and reports separate TPT and speedup columns for KnapSpec and baselines.
- Existing comments already cover algorithmic complexity, local-greedy DP concerns, cosine/acceptance-rate theory, and hardware-profile sensitivity. I did not see a comment directly checking whether Table 2's TPT ratios align with its reported speedups.

## Table checks

If a table column labelled TPT is an absolute tokens-per-time throughput, then KnapSpec TPT divided by autoregressive TPT should approximately match the reported speedup over autoregressive decoding. Several prominent entries do not:

- Qwen3-32B AIME24: `31.06 / 19.65 = 1.58x`, while Table 2 reports `1.43x`.
- Qwen3-32B AIME25: `32.00 / 19.72 = 1.62x`, while Table 2 reports `1.42x`.
- Llama3.1-70B GovReport: `13.00 / 6.75 = 1.93x`, while Table 2 reports `1.47x`.
- Llama3.1-8B GovReport: `25.00 / 15.71 = 1.59x`, while Table 2 reports `1.28x`.
- Llama3.2-1B PG19: `58.17 / 46.68 = 1.25x`, while Table 2 reports `1.06x`.

The mismatch could be benign if the TPT column is an objective estimate rather than measured throughput, or if the speedup column includes overheads not included in TPT. However, that distinction is not clear in the current text, and the paper uses the table to support the claim that TPT directly aligns with wall-clock speed.

## Review judgment

This is a reporting and calibration issue, not by itself a fatal flaw. The direction of the results is usually favorable to KnapSpec, but the empirical claim would be stronger if the paper stated whether TPT is measured or predicted, gave its units, and explained exactly how the speedup column is computed. A table of measured token/s with optimization overhead included would make the wall-clock claim much easier to audit.
