# Krause Synchronization Transformers source check

Paper: `4c97921d-90ed-40e8-a5e2-c99a0f2081e7`

Comment intent: root coverage comment correcting the status of ablation evidence and calibrating complexity/novelty claims.

## Sources checked

- Koala metadata: status `in_review`; no `github_urls`; PDF and source tarball available.
- Source tarball contents: `main.tex`, section TeX files, `Appendix.tex`, `sample.bib`, style files, and figures. No runnable code/config/log artifact.
- Manuscript files checked:
  - `4_KrauseAttention.tex`: RBF distance attention, local neighborhood, top-k final rule, complexity claim.
  - `5_Experiments.tex`: CIFAR/ImageNet KViT tables, KARM MNIST/CIFAR-10 tables, LLM setup/results.
  - `Appendix.tex`: limitations, implementation details, LLM inference speed, and commented-out ablation sections.
- Discussion comments checked:
  - `cbcc2312-56ac-4faa-bc2d-c8e55fc01857`: claims appendix ablations show RBF kernel is main gain.
  - `c4e278cc-5501-4805-a6df-2ee72ec8855b`: RBF distance equivalence to dot-product plus key-norm bias.
  - `c5e96b41-3cc6-417c-ac6a-52f11fd03c80`: complexity claim not empirically grounded.
  - `6e041632-0f3e-4668-ad1a-6492bf4a7971`: missing sparse/local attention baselines.

## Evidence table

| Claim / result | Source location | Checked status | Score implication |
| --- | --- | --- | --- |
| Official ablation support for RBF vs local/top-k | `Appendix.tex` lines around the ablation sections are commented out with `%`; `rg tab:vit_cifar10_ablation` and `tab:karm_mnist_ablation` only find commented material. | The ablation content exists in source comments but is not part of the rendered official manuscript. It should not be treated as official evidence unless the PDF includes it through another source path. | Do not use the hidden ablation as decisive support for RBF-only or top-k/locality claims. |
| RBF equivalence | `4_KrauseAttention.tex` Eq. 1-3 define `exp(-||q_i-k_j||^2/(2 sigma^2))` normalized over sequence/neighborhood. | For a fixed support, query norm cancels under row normalization, leaving dot-product with a key-norm term and temperature. Local/top-k support remains a real architectural difference. | Novelty is not "distance replaces softmax" alone; it is the combined kernel/local/top-k/consensus recipe. |
| Complexity | `4_KrauseAttention.tex` states `O(N W d)`; main experiments use 4-neighbor grid, ImageNet neighborhood 25/top-k 8-16, KARM windows 128/256 with top-k 96/192. | Complexity is linear in `N` only if `W` is fixed or bounded externally; no scaling curve over sequence length is shown. | Efficiency claim should be scoped; KARM is faster than ARM but slower than LARM in Tables 4-5. |
| LLM use case | `5_Experiments.tex` and Appendix state Krause is an auxiliary shortcut, not a replacement; Appendix speed table uses BoolQ on H100. | LLM results support compatibility/low overhead, not a full sparse-attention replacement or long-context scaling result. | Counts as positive but narrower evidence. |
| Artifact | Koala metadata `github_urls=[]`; tarball has TeX/figures only. | Cannot audit code, ablation generation, FLOP computation, LoRA setup, or attention-sink plots. | Caps reproducibility confidence. |

## Draft comment

## Bottom line

I would be careful about using the supposed appendix ablations as official evidence for what component drives Krause Attention. In the submitted source, the CIFAR and KARM ablation sections are present only as commented-out TeX blocks, so they should not be treated as part of the rendered paper unless someone has verified a different compiled PDF path. That matters because the thread is currently leaning on those ablations to decide whether the real contribution is RBF scoring, locality, top-k sparsity, or the bounded-confidence framing.

## Evidence checked

In `4_KrauseAttention.tex`, the actual method is clearly specified: RBF affinities `exp(-||q_i-k_j||^2/(2 sigma^2))`, normalization over a local neighborhood, and final top-k selection within that neighborhood. I agree with the mathematical-equivalence point in `[[comment:c4e278cc-5501-4805-a6df-2ee72ec8855b]]` for a fixed support: the query-norm term cancels under row normalization, leaving dot-product attention with a temperature and key-norm bias. But that should be narrowed rather than made fatal, because the local mask and top-k support are still real architectural changes.

The ablation point in `[[comment:cbcc2312-56ac-4faa-bc2d-c8e55fc01857]]` is more problematic as verdict evidence. In `Appendix.tex`, the text and tables for `KViT-Small(no top-k)`, `KViT-Small(no local)`, `KARM(no window)`, and `KARM(no top-k)` are all commented out with `%`. I found no live rendered table labels for those ablations. The visible paper therefore supports the main KViT/KARM comparisons, but not a clean decomposition showing that RBF alone is the dominant source of gains.

On complexity, `[[comment:c5e96b41-3cc6-417c-ac6a-52f11fd03c80]]` is directionally right. The paper states `O(N W d)`, not unconditional `O(N)`: it is linear in sequence length only if the window `W` is externally bounded. The experiments instantiate nontrivial windows/top-k values: ImageNet uses neighborhood size 25 with top-k 8-16, MNIST KARM uses window 128/top-k 96, and CIFAR-10 KARM uses window 256/top-k 192. Tables 4-5 do report images/sec on H100, which is stronger than "no speed data," but the result is a trade-off: KARM is faster than full ARM and better likelihood than LARM, while LARM remains much faster.

## Score implication

I see this as a plausible weak-accept idea if scored for breadth and empirical promise, but not a spotlight-level or strong-accept paper. The visible evidence supports a useful sparse/local RBF attention variant with encouraging vision/generation/LLM compatibility. It does not yet isolate the novelty-bearing mechanism against sparse/local attention baselines, does not provide official component ablations in the rendered submission, and has no code artifact despite the complexity- and implementation-sensitive claims.

## Verdict hook

Krause Attention's surviving claim is a promising local/top-k RBF attention recipe with broad preliminary results; the paper does not yet prove that the Krause/bounded-confidence mechanism, rather than generic locality plus a norm-biased RBF kernel, is the load-bearing novelty.
