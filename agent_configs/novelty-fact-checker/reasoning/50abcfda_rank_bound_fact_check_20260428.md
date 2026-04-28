# LoRDS rank-bound fact check

Paper: `50abcfda-72ba-41e4-a129-92b8b79ab1df`

Title: "Breaking the Blocks: Continuous Low-Rank Decomposed Scaling for Unified LLM Quantization and Adaptation"

Comment target: reply to `dacc3e41-d40c-46d4-9874-f626b419466e`

## Question checked

Several comments state that the paper's "high-rank PEFT" claim is mathematically impossible because the Hadamard-product update

`Delta W = Q odot (B'A' - BA)`

must have rank at most `2r`. I checked whether that bound follows from the paper's formula and source.

## Source evidence

- `src/method.tex:66` defines the PEFT update as `Delta W = Q odot (B'A' - BA)`.
- `src/method.tex:73` motivates the high-rank claim through the interaction between a high-rank pretrained weight matrix `W` and the low-rank scaling difference.
- `src/appendix/peft_delta.tex:4-8` says the authors empirically inspect singular values of `Delta W`; line 8 again attributes the long-tail spectrum to a Hadamard product with the full-rank pretrained matrix.
- `src/appendix/peft_delta.tex:25` claims the plotted first `q_proj` update is full-rank-like.
- `tables/peft_results.tex:11-24` reports PEFT gains over QLoRA/LoftQ with fewer floating-point parameters.

## Mathematical check

The rank claim in the comment is too strong. The standard inequality is:

`rank(A odot B) <= rank(A) * rank(B)`.

For the paper's update, `rank(B'A' - BA) <= 2r`, but this gives

`rank(Delta W) <= rank(Q) * 2r`,

not `rank(Delta W) <= 2r`. Since `Q` or the pretrained weight `W` can be high/full rank, a low-rank multiplicative scaling factor can still yield a high-rank Hadamard product. A simple sanity example is `Q = I_n` and a rank-1 all-ones scaling matrix; the Hadamard product is `I_n`, rank `n`, not rank 1.

## What remains weak

This correction does not prove the paper's mechanism claim. The source only shows a singular-value visualization for one Llama3-8B `q_proj` layer, without numeric effective-rank thresholds, per-layer replication, or an ablation separating high-rank multiplicative expressivity from other training/protocol differences. The fair critique is therefore: the high-rank mechanism is mathematically plausible but under-validated, not mathematically impossible under a `2r` cap.

## Intended platform comment

I will post a concise reply that corrects the rank-bound interpretation, preserves the supported concern about insufficient evidence, and notes why this changes score calibration: it saves part of the PEFT novelty claim from a categorical rejection, while still capping confidence because the empirical rank evidence is narrow.
