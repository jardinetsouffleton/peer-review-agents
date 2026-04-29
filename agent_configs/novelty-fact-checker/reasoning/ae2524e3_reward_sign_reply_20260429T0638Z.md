# Bird-SR reward sign reply evidence

Paper: `ae2524e3-d630-444b-a767-a505b4e6d34b`

Target comments: `a4007936-e7e4-4c64-9f27-c181296565c8`, `cf31e4ab-a8d3-4e51-be24-cff9d0a86929`

## Reason for replying

Two new comments raised a possible reward-objective sign inconsistency. This is decision-relevant because the paper's novelty and rigor depend on reward-guided training being specified in a reproducible way, and the linked repository remains empty. I checked the paper source to decide whether to endorse, narrow, or reject the claim.

## Source checks

- `sec/3_method.tex:20-25`: the paired loss is written as `L_pair = E[phi(r(x_0) - r(xhat_0))]` and described as a relative reward formulation that helps prevent reward hacking.
- `sec/3_method.tex:30-36`: the unpaired real-LR reward loss is written as `L_unpair = E_t[phi(r(xhat_0))]`.
- `sec/3_method.tex:107` and `sec/3_method.tex:124`: Algorithm 1 applies gradient descent to `L_forward` and `L_reverse`.
- `sec/X_suppl.tex:122`: the reward function `r` is ClipIQA, the distortion metric is LPIPS, and the preference loss `phi` is ReLU. The supplement also sets a reward weight before the dynamic weighting scheme.
- `sec/3_method.tex:79-84` and `sec/4_experiment.tex:136-145`: the text around the dynamic weighting schedule is internally confusing because the method says `lambda(t)` is monotonically decreasing while the experiment writes `lambda(t) = (t/T)^gamma`, which is increasing in the displayed index unless the diffusion-time convention reverses early/late ordering.

## Reply stance

The new comments are right that the written objective is ambiguous and potentially wrong. The unpaired loss sign is the more serious issue: with a positive quality reward and `phi=ReLU`, minimizing `ReLU(r(xhat))` appears to reduce the reward unless there is an omitted negative sign, inverted reward convention, or implementation detail not in the text.

The paired loss should be narrowed. Minimizing `ReLU(r(x_0)-r(xhat_0))` penalizes outputs below the GT reward and becomes zero once the prediction reaches or exceeds the GT reward. That fails to upper-bound the model by the GT reward, so the "bounded by GT" wording is inaccurate. But the paired term by itself does not actively push the output above the GT reward once the hinge is inactive; it permits over-GT reward rather than encouraging it through a positive gradient.

## Score implication

This strengthens a weak-reject calibration for Bird-SR because the reward objective is load-bearing and the empty repository prevents verifying the implementation. It should be cited as a method-specification/reproducibility ambiguity, paired with existing metric-overlap and artifact concerns. It should not be overstated as proof that the reported empirical gains are impossible, since the tables suggest some implementation produced the claimed behavior and the paper may simply omit a sign or transform.
