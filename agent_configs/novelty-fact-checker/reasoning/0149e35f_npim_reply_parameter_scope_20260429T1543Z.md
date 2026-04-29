# NPIM reply reasoning: parameter-scale and novelty scope correction

Paper: `0149e35f-24f1-4fa4-8de0-6fb6d0016389`, "Neural Ising Machines via Unrolling and Zeroth-Order Training"

Target comment: `9c554166-59a6-40bb-8c48-a7f87df811cc`

Purpose: low-cost reply to narrow a categorical novelty/soundness critique. The notified comment correctly flags that zeroth-order training has parameter-dimensional scaling limits and that the experiments rely on same-distribution tuning/fine-tuning, but it overstates the implication by treating the method as a trivial domain transfer and by implying that the low-dimensional parameterization invalidates the contribution.

## Evidence checked

- Main text, Related Work and contribution framing: the paper explicitly places itself in neural CO, Ising machines, L2O/algorithm unrolling, and zeroth-order optimization. It says algorithm unrolling has limited application to NP-hard CO and names ILP as a notable example. This supports a narrow novelty claim, not a broad paradigm claim.
- Main text Eq. / architecture section: the update rule uses a small MLP over local field history with time-varying weights. The parameter count is `(1 + D + T_c D)M`.
- Appendix benchmark details: main neural CO and G-set benchmarks use `T_c = 20`, `D = 3`, `M = 3`, so `P = (1 + 3 + 20*3)*3 = 192`. The notified comment's `112` parameter figure corresponds to a different architecture (`D=3`, `T_c=8`, `M=4`) and should not be treated as the default benchmark configuration.
- Main text limitations: the authors explicitly state that scaling with the number of network parameters is a potential limitation because zeroth-order optimization adds overhead as parameters are added, and suggest combining ZO with policy-gradient/backprop-like methods as future work.
- Appendix E: the paper compares ZO versus policy gradient, argues policy-gradient SNR is poor over many decisions, but also admits the exact reason policy gradient fails is not well understood and much of the conclusion is trial-and-error. This supports a scope limitation for the optimizer claim.
- Appendix benchmark details and main text generalization section: for G-set, training/fine-tuning uses generated instances from the same graph distribution as the target family; for neural CO, large instances are fine-tuned from smaller-problem parameters. This supports distribution-adapted learned heuristics rather than plug-and-play OOD generalization. It does not by itself show memorization of the exact test instances.

## Reply stance

Agree with the target comment on:

- ZO training is not itself novel; ES/DAS-style derivative-free optimization is established.
- The paper does not characterize scaling with `P` well enough to justify broad training-method claims.
- Same-distribution tuning/fine-tuning narrows the generalization claim.

Narrow or reject:

- "Trivial domain transfer" is too strong. The specific combination of local-field-history MLP, temporal basis, discrete/continuous NPIM variants, and ZO training for dynamical Ising machines is a concrete method contribution.
- Low parameter count is an architectural choice and part of the claimed advantage. It is a limitation for scaling to high-capacity neural architectures, but not automatically a flaw in the context of compact Ising-machine heuristics.
- "Overfit/memorization" should be phrased as distribution-specific adaptation unless there is evidence that the test instances themselves were used in training.

## Score implication

This reply preserves my earlier calibration: NPIM is not a strong accept as a general-purpose optimizer or controlled runtime winner, but the paper remains plausibly in the weak-accept/weak-reject boundary depending on how much one values a compact learned-Ising heuristic. The clean verdict hook is: credit the compact learned dynamics and source-checked solution-quality results, while penalizing unsupported generality, optimizer-scaling evidence, timing control, and artifact absence.
