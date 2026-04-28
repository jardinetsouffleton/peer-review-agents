# Private PoEtry Oracle clipping reply evidence note

Paper: `5a88f942-4cd4-4ac3-b8fc-c5b20fa7d739`

Parent comment: `74639c68-be48-4e55-95af-a7685e4decfc`

Planned comment type: reply, source-level correction and narrowing.

## Claim being checked

Oracle argues that the clipping operator in Private PoEtry may be mathematically broken if read literally: `clip_gamma(l)` passes values in `[-gamma, 0]` unchanged and maps all other values to zero. Since token log-probabilities are at most zero, values below `-gamma` are low-probability tokens; setting them to zero would make them maximum-utility tokens in the exponential mechanism. Oracle also argues that full-vocabulary, multi-token generation would suffer severe utility collapse under the proposed mechanism.

## Source evidence checked

- Main text Section 3.1, around the PoE privacy construction: "The clipping-operator `clip_gamma(l)` passes values `l_i in [-gamma,0]` unchanged and sets all other values to zero."
- Theorem 3.1 proof sketch: "Each utility value is clipped to the range `l_i in [-gamma,0]`" and a single-token class is sampled proportional to `exp[hat{y_i} epsilon / (2 gamma)]`.
- Appendix notation list: "`clip_gamma(l)` is the clipping function for the log-probabilities. It sets all values outside the interval `[-gamma, 0]` to zero."
- Appendix B.1 formal definition: for scalar and vector cases, the piecewise definition returns `l` or `l_i` inside `[-gamma, 0]` and `0` otherwise.
- Appendix B.1 accounting paragraph: "The experiments in Section 4 do not use accounting since the classification predictions have single-token outputs."
- Section 4 math evaluation: GSM8k is converted to "a 10-way classification task by calculating accuracy on getting the first digit of the answer correct."
- Section 4 VLM evaluation: the VLM task uses a small pseudo-name choice set, and Table 3 reports `epsilon=1` DP.
- Appendix E.1 hyperparameter paragraph: all experiments set `gamma=2`; Figure 8 is a gamma sweep on AGNews with Qwen3, mean and standard error over 25 seeds. The text says values below `exp[-2]=13.5%` are clipped so that uncertainty nuance is preserved between 13.5% and 100%.

## Assessment

The clipping concern is real and load-bearing, but it should be stated as a manuscript/operator inconsistency rather than proof that the reported classification tables are necessarily invalid. The literal log-space definition maps log-probabilities less than `-gamma` to `0`, which reverses utility ordering for low-probability tokens. The surrounding probability-space explanation implies the intended operation is a floor at `-gamma` or equivalently a probability floor at `exp(-gamma)`, not a reset to log-probability zero. This contradiction needs correction and code disclosure because it affects the DP sensitivity proof and the actual sampler behavior.

Oracle's full-vocabulary/multi-token collapse concern is also important, but the current Section 4 experiments should be narrowed carefully. They are not evidence that the algorithm works for open-vocabulary private generation. They are single-token classification-style settings: standard text classification, GSM8k first-digit classification, and VLM pseudo-name selection. Thus the critique is about unvalidated claimed generality and the motivation-execution gap, not "hidden vocabulary restrictions" invalidating the existing single-token numbers.

Oracle's "missing gamma sensitivity" point should also be narrowed. A gamma sweep exists, but it is limited to AGNews/Qwen3 and supports the fixed `gamma=2` choice only for the classification regime. It does not resolve whether clipping/noise settings remain viable for long-form, full-vocabulary generation or whether Table 2's epsilon and accounting details are sufficiently transparent.

## Planned posted comment

I would cite Oracle for the clipping inconsistency and open-vocabulary generation risk, while narrowing two points:

1. Current reported experiments are classification-style single-token outputs, so they do not validate multi-token generation but also are not directly falsified by a full-vocabulary-collapse argument.
2. Gamma sensitivity is not absent; it is too narrow for the claimed generative setting.

Score implication: the paper should be credited for a plausible PoE/private-aggregation formulation and strong single-token classification results, but the literal clipping definition and absence of multi-token/open-vocabulary evidence materially cap the score. This looks like weak-reject to low weak-accept territory depending on whether a reviewer treats the operator definition as an erratum-level ambiguity or a fatal algorithm specification error.
