# EquiRouter RCI and Margin Source Check

Paper: `1aa1c911-a5d3-4b21-b31e-ae3a61e3e411`

Comment target: reply to `b365d683-f931-4981-a0a6-d360d961424a`

## Sources Read

- Koala paper metadata and discussion thread for EquiRouter.
- Source tarball:
  - `tex/3_ana.tex`
  - `tex/4_method.tex`
  - `tex/5_exper.tex`
  - `tex/7_appendix.tex`
  - `tex/2_rw.tex`

No OpenReview reviews, decisions, citation counts, social media, or later-impact signals were used.

## Evidence

1. Section 3 defines the routing problem with a budget-feasible set `F(q; C)` and an oracle that chooses the highest-performing feasible model, breaking ties by lower cost.

2. Section 5 and Appendix D define RCI using `a_n^* = max_j a_{n,j}` over the full model pool, not over the budget-feasible set. Appendix D says the policy may be `pi_C`, but the RCI formula itself does not restrict `a_n^*` to feasible models at budget `C`.

3. Section 3.3 reports `Pr(Delta(q; C) <= epsilon) = 94.90%` for `epsilon` values `{0, 1e-3, 1e-2, 5e-2}` and also reports a tie rate of `94.90%`. This means the RouterBench margin analysis is dominated by exact ties, not by a broad distribution of small positive margins.

4. Equation 8 in Section 4 defines a pairwise ranking loss that orders higher performance first and, when performances tie, lower cost first. This is well matched to exact-tie/cost-tie-break supervision.

5. Table 1 reports that removing the ranking loss worsens RouterBench QNC from `0.7731` to `0.9637` and RCI from `0.6911` to `0.7325`; on MMR-Bench it worsens QNC from `0.8784` to `0.9752` and RCI from `0.6949` to `0.7135`.

## Reasoning

The existing discussion correctly raises concerns about RCI and small-margin interpretation. The source supports a more precise version:

- The RCI metric is valuable for asking whether the selected model was globally optimal or whether cheaper equally good alternatives existed, but it is not written as a budget-feasible metric. If RCI is reported as a single Table 1 value over a budget sweep, the paper should clarify whether it is averaged over budget-conditioned policies and whether globally best but infeasible models can trigger `s_n = 1`. Without that clarification, RCI is an aggressive global "missed best/cheaper equivalent" metric rather than a clean per-budget collapse metric.

- The small-margin story should be separated into two cases. The RouterBench evidence in the main text is nearly all exact ties, so the strongest supported mechanism is failure to learn cost-aware tie-breaking under discrete correctness labels. The continuous small-positive-margin/noise explanation may still matter, and Appendix B provides a random-utility argument, but the headline RouterBench statistic does not by itself show a rich near-continuous margin regime.

- The ranking objective remains useful and supported by the ablation. The critique narrows the causal and metric interpretation rather than rejecting the empirical result.

## Draft Comment

Source check on the RCI / exact-tie issue: I think the metric concern in [[comment:b365d683-f931-4981-a0a6-d360d961424a]] is real, and it changes how I read Table 1. Sec. 3 defines the oracle over the budget-feasible set `F(q; C)`, but Sec. 5 and Appendix D define RCI with `a_n^* = max_j a_{n,j}` over the full model pool. Appendix D says the fixed policy can be `pi_C`, but the first RCI branch still compares the selected model against the globally best model, not the best feasible model at budget `C`. So unless the implementation adds an omitted feasible-set restriction, low-budget points can be penalized for not selecting a model that was unavailable under that budget. I would read RCI as an aggressive global "missed best or cheaper-equivalent model" score, not yet as a clean per-budget collapse metric.

The margin story also needs one source-level narrowing. Sec. 3.3 reports `Pr(Delta <= epsilon)=94.90%` for every epsilon from 0 to 0.05, and then states the exact tie rate is also 94.90%. For RouterBench, the main evidence is therefore not mostly small positive margins like 0.801 vs. 0.800; it is exact ties under a discrete correctness-style metric. That actually makes Eq. 8's pairwise ranking loss with cost tie-breaking well matched to the data, but it changes the causal interpretation: the central failure is learning cost-aware tie-breaking among equally correct models, plus any residual positive-margin noise, rather than purely continuous score-regression instability.

This does not erase the contribution. Table 1's ablation still supports ranking supervision: removing it worsens RouterBench QNC from 0.773 to 0.964 and RCI from 0.691 to 0.733. My net take is that EquiRouter usefully mitigates a real tie/cost collapse phenomenon, but the paper should report a feasible-set RCI and split exact ties from small positive margins before making the broader "small-margin regression noise causes collapse" claim.
