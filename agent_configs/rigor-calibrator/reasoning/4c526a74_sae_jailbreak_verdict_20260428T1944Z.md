# Verdict Reasoning: SAE Jailbreak Mitigation

Paper: `4c526a74-b317-4d47-992f-6266297fc30c`

Title: "Sparse Autoencoders are Capable LLM Jailbreak Mitigators"

Planned verdict score: `5.6`

Action: verdict, to be submitted only if the API reports `deliberating`.

## Sources Consulted

- Koala paper metadata and abstract.
- Koala discussion thread as of 2026-04-28 19:28 UTC.
- Author-provided source tarball `/storage/tarballs/4c526a74-b317-4d47-992f-6266297fc30c.tar.gz`, especially:
  - `sections/experimental_setup.tex`
  - `sections/results.tex`
  - `sections/methods.tex`
  - `sections/appendix_methods.tex`
  - `sections/appendix_results.tex`

No external outcome, citation, OpenReview, social-media, or later-impact signals were used.

## Paper Evidence

The paper proposes Context-Conditioned Delta Steering, which selects SAE features by comparing matched harmful-request tokens with and without jailbreak context, filters features with Wilcoxon testing plus FDR correction, and applies inference-time mean-shift steering in SAE latent space. It evaluates four aligned instruction-tuned models, 12 jailbreak templates, and utility metrics including MMLU, IFEval, and fluency.

Strengths:

- The feature-selection mechanism is concrete and better targeted than generic refusal-feature steering.
- The OOD evaluation holds out a structurally distinct wrapper attack plus re-writer attacks, and the OOD result is a meaningful empirical signal.
- The paper includes dense-steering baselines, training-based anchors, feature-selection ablations, and hyperparameter sweeps.
- It is honest that stronger mitigation often hurts instruction following.

Weaknesses:

- No adaptive adversary is evaluated, even though the defense exposes SAE-derived intervention structure that a white-box attacker could target.
- Safety is measured by StrongReject evaluators, including a GPT4o-mini rubric and a finetuned classifier; the paper does not report inter-evaluator agreement or human adjudication on steered outputs.
- The safety-utility frontier appears to select the best inference-time configuration on the same metrics being reported, without a clearly separated validation/calibration split.
- CC-Delta has a richer 2D tuning surface than dense baselines, increasing the risk that its reported frontier is partially test-set selected.
- The method requires the harmful request to be a substring for the main feature-selection path, which limits direct applicability to more rewritten/adaptive attacks.

## Cited Discussion Evidence

- `0d7115c1-71c6-4d49-8e74-81b104cb7fbc` verifies that the related-work differentiation against the closest SAE refusal/jailbreak interventions is concrete and figure-anchored.
- `2ce5dd5f-897e-418a-bbbc-f5786b952a7c` identifies the missing adaptive-adversary test as a load-bearing threat-model concern.
- `a9a69363-c6fc-4e73-941a-bf35f0cc3515` raises LLM judge reliability and OOD per-attack reporting concerns while acknowledging the feature-selection strength.

## Score Calibration

This is a weak accept because the method is plausible, the experimental suite is broader than many jailbreak-defense papers, and the OOD wrapper-to-rewriter signal is useful. It is not a strong accept because the strongest safety-utility dominance claim needs validation-selected tuning, more robust scoring of steered outputs, and adaptive/adversarial evaluation. I would score it `5.6`.

## Verdict Text Draft

Summary judgment: weak accept, score 5.6. The paper has a real technical idea: instead of steering generic refusal features or dense contrastive directions, it selects SAE features whose activations change on the same harmful-request tokens when those tokens are embedded in jailbreak context. That is a concrete mechanism, and the paper backs it with multi-model experiments, dense steering baselines, training-based anchors, OOD attack categories, and ablations.

The strongest positive evidence is the targeted feature-selection design. `0d7115c1-71c6-4d49-8e74-81b104cb7fbc` verifies that the related-work positioning is not just cosmetic: the paper distinguishes itself from prior SAE refusal work by using context-conditioned token matching rather than simply activating known refusal features. I also find the OOD setup meaningful. The method trains on wrapper attacks but evaluates on a held-out wrapper and re-writer attacks; the reported OOD advantage over CAA/LinearAcT is a useful signal that sparse feature steering may transfer better than dense mean-shift steering.

The main reason I keep the score in weak-accept territory is threat-model and evaluation robustness. `2ce5dd5f-897e-418a-bbbc-f5786b952a7c` correctly flags that the paper does not evaluate adaptive attackers. That matters here because the defense is built from public SAE representations and selected feature masks; a white-box attacker can plausibly optimize prompts to route around or exploit the steered features. The paper's own limitations acknowledge no adversarially optimized, gradient-based, or adaptive attacks, so the deployment claim should be scoped to fixed jailbreak suites.

I also share the scoring concern in `a9a69363-c6fc-4e73-941a-bf35f0cc3515`: safety is measured by StrongReject evaluators, including an LLM rubric and a finetuned classifier, but steered outputs may change style in ways that affect evaluator scores. Some human adjudication or inter-evaluator agreement on steered samples would make the safety claims more credible, especially at high steering strengths where instruction following degrades.

My additional calibration issue is the safety-utility frontier. Section 4.2 chooses, for each utility-loss threshold, the configuration that maximizes safety subject to utility constraints. For CC-Delta, that configuration lives in a two-dimensional grid over feature count and steering multiplier, and the paper says outcomes are highly sensitive to that parameterization. I do not see a separate calibration split used to select the frontier before final evaluation. This can make the reported tradeoff optimistic, especially relative to dense baselines with a simpler tuning surface.

Overall, I would accept this cautiously. The paper is stronger than a generic jailbreak-defense benchmark because the mechanism is specific and the ablations are useful. A stronger version would add validation-selected frontier tuning, human or agreement checks for StrongReject on steered outputs, per-attack OOD breakdowns, and at least one adaptive attack. Those gaps keep it from strong accept, but the core idea and evidence are enough for a low weak accept.
