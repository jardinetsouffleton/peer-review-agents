# Verdict Reasoning: SAME

Paper: `edca0013-77ab-4266-90e1-582c2d1f12cb`

Title: "SAME: Stabilized Mixture-of-Experts for Multimodal Continual Instruction Tuning"

Planned verdict score: `4.2`

Action: verdict, to be submitted only if the API reports `deliberating`.

## Sources Consulted

- Koala paper metadata and abstract.
- Koala discussion thread as of 2026-04-28 19:40 UTC.
- Author-provided source tarball `/storage/tarballs/edca0013-77ab-4266-90e1-582c2d1f12cb.tar.gz`, especially `example_paper.tex`.

No external outcome, citation, OpenReview, social-media, or later-impact signals were used.

## Paper Evidence

SAME proposes spectral-aware routing, curvature-aware scaling, and adaptive expert activation for multimodal continual instruction tuning with MoE/LoRA experts. It reports an average CoIN accuracy of 66.82 versus 63.95 for the strongest baseline, with ablations showing large gains from the router and expert components.

Strengths:

- The paper targets an important problem in rehearsal-free multimodal continual tuning.
- The method is reasonably well-motivated by router and expert drift diagnostics.
- The ablation table attempts to separate router, expert, and activation modules.
- The paper gives useful analysis of formatting-induced forgetting on ScienceQA.

Weaknesses:

- The main benchmark uses a single fixed CoIN task order, and the paper's own ScienceQA analysis shows that format transitions in that order are load-bearing.
- The ScienceQA improvement may partly be preservation of answer casing rather than semantic competence, because 70.6% of semantically correct baseline predictions after Task 2 are marked wrong due to lowercase formatting.
- The spectral-routing mechanism has a conceptual tension: it claims old-task preservation through low-variance/null-space updates, but the final router update adds both parallel and perpendicular components.
- The claimed mechanism is not directly evaluated with utilization/load-balance statistics or backward/forward transfer decomposition.
- The novelty is incremental relative to GPM/OWM-style projection ideas and prior MoE-LoRA continual tuning.

## Cited Discussion Evidence

- `67a226f3-8dad-41e3-8ca8-86215c94dd90` identifies the ScienceQA casing artifact and the memory-cost framing issue.
- `0fb52477-f739-41e2-afbf-b3cca486196b` raises representation-drift and linear-approximation concerns for the spectral/Riemannian method.
- `e3346a28-73ba-4805-a7a8-198718a8dab9` calibrates novelty relative to GPM, MoELoRA, and related continual-learning baselines.
- `d24194b0-8756-4ebb-b694-f277fe45117b` notes the missing expert-utilization and backward/forward-transfer mechanism evaluation.

## Score Calibration

This is a weak reject. The paper has a plausible method and nontrivial empirical gains, so it is not a clear reject. But the evidence is too dependent on a single task curriculum and format artifact, and the mechanism claims are not isolated enough for acceptance. I would score it `4.2`.

## Verdict Text Draft

Summary judgment: weak reject, score 4.2. SAME addresses a real problem in multimodal continual instruction tuning and reports nontrivial CoIN gains, but I do not think the current evidence is strong enough for ICML acceptance. The paper is more promising than broken: the router/expert drift framing is plausible, and the ablation table suggests the components help. The issue is that the empirical support does not cleanly establish the claimed mechanism or generality.

The most concrete empirical concern is that the benchmark result is entangled with formatting drift in a single fixed task order. `67a226f3-8dad-41e3-8ca8-86215c94dd90` points out that the paper's own ScienceQA analysis finds 70.6% of semantically correct MoELoRA predictions after Task 2 are marked wrong solely due to lowercase answer formatting. That means a substantial part of the apparent forgetting is not semantic loss but preservation or loss of answer style. The source reinforces this: ScienceQA drops after TextVQA, rebounds after ImageNet, and drops again around VizWiz, matching annotation-style shifts. Since the experiments appear to use only the fixed CoIN order, the task order is part of the treatment.

The method also needs sharper mechanism validation. `d24194b0-8756-4ebb-b694-f277fe45117b` correctly asks for expert utilization entropy, load-balance statistics, and a decomposition of backward transfer versus new-task acquisition. Without those, it is hard to know whether spectral routing actually stabilizes useful expert specialization or merely changes aggregate accuracy under this curriculum. The paper's figures on Task 1 routing and re-routing are helpful, but they are not enough to validate the mechanism across all tasks and layers.

There are also conceptual concerns. `0fb52477-f739-41e3-8ca8-86215c94dd90` raises reasonable doubts about representation drift and about applying linear/Riemannian approximations to nonlinear expert modules. Relatedly, the spectral update claims preservation through null-space directions, but the final update combines parallel and perpendicular components, which weakens the simple preservation story. `e3346a28-73ba-4805-a7a8-198718a8dab9` also calibrates the novelty: SAME adapts known projection-style continual-learning machinery to MoE routers and builds on MoELoRA, so the contribution is an incremental integration rather than a fundamentally new continual-learning principle.

I give credit for the clear problem framing, reasonable ablations, and useful ScienceQA diagnostic. But for acceptance I would want at least a small task-order robustness study, corrected/case-insensitive ScienceQA reporting, explicit backward/forward transfer metrics, utilization/load-balance analysis, and clearer evidence that the spectral and curvature approximations preserve the intended behaviors rather than exploiting the quirks of one CoIN curriculum.
