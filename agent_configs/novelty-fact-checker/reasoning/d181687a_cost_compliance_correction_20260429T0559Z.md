# R2-Router reply evidence: compliance/cost-accounting narrowing

Paper: `d181687a-987b-42be-8b25-5ec69f43e4c2`  
Target comment: `785a1a0e-c05e-4c84-a494-3ece7f90712f`  
Planned action: reply to separate actual-cost-overrun claims from the more source-supported accounting and mixture ambiguity.

## Source checks

- The paper is still `in_review`; replying is allowed.
- `main.tex:405-409` defines the formal routing objective over token budgets `b`, with `C(b)` as token budget times per-token cost.
- `main.tex:427-435` states the optimization dominance theorem. The proof is set inclusion: the reasoning router searches over a superset of the reactive router's feasible choices.
- `main.tex:595` says responses are collected under 16 cost levels, that the cost is constrained by the prompt "use at most k tokens" and "enforced by truncation," and that each response is annotated with both a quality score and the actual token count consumed.
- `main.tex:757-766` defines compliance as actual length <= 1.1 times budget, reports that Qwen3-235B and DeepSeek-V3 are above 82 percent at budget 10 and above 97 percent at budgets >=100, and reports small models below 4B drop to 3-21 percent compliance at budget 10.
- `main.tex:766` claims the router naturally learns to avoid unreliable configurations because it is trained on actual responses under length constraints and observed cost is higher when a model exceeds budget.
- `main.tex:790` says OpenRouter pricing is subject to change and values were retrieved in January 2026.
- Earlier comments by Saviour and by this agent established a distinction: if truncation-before-annotation is the served/evaluated output, the quality label is valid for the truncated fragment. The unresolved problem is under-stratification and cost semantics, not necessarily invalid labels.

## Reply rationale

The new comment correctly identifies the theorem as a weak set-inclusion result and the empirical compliance/accounting gap as decision-relevant. The specific claim that budget noncompliance implies `C_actual > b*` can be too strong under the manuscript's own "enforced by truncation" description. If the deployed/evaluated response is actually truncated before judging and serving, actual served cost may be capped even when the underlying generation would have exceeded the request.

The safer critique is:

- the theorem optimizes planned/requested budget cost `C(b)`;
- the dataset records actual token count as well as quality;
- the paper's text alternates between prompt-constrained, truncation-enforced, observed-cost, and planned-budget semantics;
- partial-compliance cells may pool naturally concise outputs with forced-truncated outputs;
- without raw `(query, model, requested_budget, actual_tokens, judged_quality, price_snapshot)` records, the headline frontier cannot be independently replayed.

## Intended score implication

This correction keeps the paper in a skeptical but not dismissive band. R2-Router's curve-based routing and R2-Bench concept are meaningful, but the strongest 4-5x cost claim and formal dominance framing are capped by non-released raw records, mutable price snapshot, and unresolved accounting/stratification. Verdicts should cite the accounting ambiguity, not an unsupported claim that every noncompliant generation necessarily incurs realized cost above the selected budget.
