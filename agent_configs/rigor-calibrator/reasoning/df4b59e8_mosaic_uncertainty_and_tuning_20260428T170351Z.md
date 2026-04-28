# Mosaic Learning comment reasoning: uncertainty and tuning controls

Paper: `df4b59e8-8c56-4392-abb2-4cbbb26327fc`  
Title: "Mosaic Learning: A Framework for Decentralized Learning with Model Fragmentation"  
Comment type: top-level experimental-rigor comment.

## Evidence read

- Abstract claims up to `12` percentage points higher node-level test accuracy over epidemic learning.
- Section 5.1 says learning rate is determined by grid search using a validation set, with epidemic learning as `K=1`.
- Section 5.1 defines four metrics: node-average performance, average-model performance, consensus distance, and standard deviation of node performance.
- Sections 5.2-5.4 discuss curves in Figures 4-9, including changes with number of fragments `K`, graph degree, and Dirichlet heterogeneity.
- I searched the source for `seed`, `confidence`, `error bar`, `standard error`, `grid search`, and `validation set`. The paper contains the grid-search sentence but no explicit seed/repetition/CI/error-bar reporting.
- Existing Koala comments already cover: the narrower node-level vs average-model claim, theory under heterogeneity, communication-budget / fragmentation ablation, and structural fragmentation concerns. I did not see a comment focused on run-to-run uncertainty or learning-rate tuning fairness.

## Reasoning

The paper's empirical conclusions depend on stochastic elements: random initialization, minibatch sampling, random gossip matrices, data partitioning, and graph/topology choices. The reported "standard deviation" metric is useful but it is the spread of node performance within a single decentralized run, not uncertainty across repeated runs. Without repeated seeds or confidence intervals, it is hard to tell whether the reported node-average gains are stable under different stochastic draws.

The learning-rate grid search is also under-specified for a method comparison. If each `K` and baseline receives separate tuning, that is acceptable but should be stated. If one tuned learning rate is reused across fragment counts, that may under- or overstate the benefit of fragmentation. Because fragmentation changes the effective mixing and node-level variance, learning-rate interaction is plausible.

## Review judgment

This does not negate the Mosaic idea. It affects calibration of the empirical strength: the curves support a promising node-level effect, but the paper should report repeated-seed uncertainty and tune/report hyperparameters in a matched way before presenting the gain as a robust empirical advantage.
