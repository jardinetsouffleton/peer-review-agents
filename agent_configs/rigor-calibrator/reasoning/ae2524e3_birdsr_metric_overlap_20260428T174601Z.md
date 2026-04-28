# Bird-SR Metric-Overlap Review Note

Paper: `ae2524e3-d630-444b-a767-a505b4e6d34b`

Title: "Bird-SR: Bidirectional Reward-Guided Diffusion for Real-World Image Super-Resolution"

Timestamp: 2026-04-28T17:46:01Z

## Evidence Read

- Read the Koala paper abstract and discussion.
- Fetched the Koala paper source tarball and inspected:
  - `sec/3_method.tex`
  - `sec/4_experiment.tex`
  - `sec/X_suppl.tex`
- Reviewed existing Koala comments to avoid duplicating already-covered concerns. Existing comments cover reward formulation asymmetry, component ablations, distribution shift, missing runnable code, and the fact that external baselines sometimes win individual metrics.

## Source Observations

- The method defines a reward-guided objective where `r` measures perceptual quality (`sec/3_method.tex`), and the implementation details in `sec/X_suppl.tex` state: "For the reward function r, we employ ClipiQA; for the distortion metric D, we adopt LPIPS."
- The main quantitative table reports LPIPS, MUSIQ, MANIQA, ClipIQA, and LIQE. Thus ClipIQA is both a direct training reward and an evaluation metric, while LPIPS is both a structural/distortion training signal and a reported fidelity metric.
- The main ablation uses MUSIQ and LPIPS. The supplementary loss-component ablation reports ClipIQA and LPIPS, which are especially close to the training objective.
- The paper includes a user study with 20 volunteers and 40 LR images across four datasets, with pairwise comparisons against a randomly selected other method. The reported preference rates are high, but the paper does not provide confidence intervals, per-dataset breakdowns, rater agreement, or enough detail to evaluate whether the image/method pairing avoids dependence across repeated judgments.
- Table 1 does not show uniform dominance across all external baselines and metrics. For example, DiffBIR and SeeSR outperform or match Bird-SR on some RealSR/DRealSR no-reference and LPIPS metrics, while Bird-SR improves its own DiT4SR and ResShift backbones consistently.

## Reasoning

The paper's reward-optimization story is plausible and the ablations support that semantic/structural constraints reduce pure reward drift. However, because the reward model and structural loss overlap with reported metrics, part of the measured improvement can reflect direct optimization of the scoreboard rather than independent perceptual improvement. This is not fatal because the authors also report MUSIQ, MANIQA, LIQE, and a user study. Still, the strongest acceptance-level evidence would come from held-out metrics not used in training plus a more statistically specified human study.

The comment should therefore focus on metric/reward overlap as a concrete rigor issue, not as a broad rejection of the method.
