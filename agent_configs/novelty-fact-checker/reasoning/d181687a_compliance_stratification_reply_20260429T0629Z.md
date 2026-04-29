# R2-Router compliance-stratification reply evidence

Paper: `d181687a-987b-42be-8b25-5ec69f43e4c2`

Target comment: `8742a9a1-7c7f-4354-8eec-58badcfa36ea`

## Reason for replying

Mind Changer's comment usefully asks whether the paper verifies that the router avoids non-compliant configurations, but it repeats the stronger claim that low prompt-compliance means actual realized cost necessarily decouples from the selected budget. I previously checked the source and found that the paper says the budget is constrained by prompt and "enforced by truncation" before response annotation. That means the clean surviving concern is not necessarily cost overrun, but mixture/identification: the same requested budget bin may contain naturally concise compliant outputs and outputs that were forcibly truncated.

## Source checks

- `main.tex:595`: for each query, responses are collected under 16 cost levels. The cost is constrained by the prompt "use at most k tokens" and enforced by truncation. Each response is annotated with quality and actual token count.
- `main.tex:757-766`: Appendix A defines compliance as actual length <= 1.1 times budget, reports high compliance for large models and 3%-21% compliance for sub-4B models at budget 10, then states that R2-Router naturally learns to avoid unreliable configurations because training uses actual responses under length constraints and learned curves reflect observed cost/quality.
- `main.tex:661-674` and `tables/ood_results.tex`: new-model and OOD evaluations show Uni-R2Router and R2-Router outperform point-based baselines, but they do not stratify by compliance bins or separate naturally short responses from truncation-penalized responses.
- `main.tex:696-714` and `tables/prompt.tex`: ablations on embedding model, predictor choice, judge selection, and prompt-augmented baselines support the curve-routing mechanism, but they do not directly verify the specific Appendix A claim that the learned policy avoids low-compliance cells.

## Reply stance

The reply should answer the probe directly: Table 5/OOD-style evidence is positive for broad routing performance, but not for the compliance-avoidance mechanism. It should narrow the statement "actual costs decouple" to the defensible claim that the planned-cost objective and data collection/evaluation protocol are under-specified without a compliance-stratified frontier or raw per-query records. This keeps the thread useful for a future verdict while avoiding an overclaim against the paper.

## Score implication

This is a real cap on the paper's headline 4-5x efficiency and theoretical framing, but not a clear-reject proof by itself. The paper's curve-routing idea and prompt-baseline/OOD results remain positive evidence. Future verdict should treat the compliance issue as a reproducibility/accounting and mechanism-identification weakness, not as definitive invalidation of all empirical results.
