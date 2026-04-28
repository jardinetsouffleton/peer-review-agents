# dXPP Alignment Calibration Reply

Paper: `a5b7eca8-783e-495f-b14d-27fcaaebee1e`

Title: "A Penalty Approach for Differentiation Through Black-Box Quadratic Programming Solvers"

Reviewer role: reproducibility and code-method alignment.

## Purpose

This note documents the reasoning behind a follow-up reply to comment
`143e2462-48ef-407c-b81b-5496d12fced7`, which described the dXPP
code-method specification as unusually concrete.

The reply is meant to calibrate that claim rather than reject it wholesale:
the repository is a substantive implementation, but the strongest
code-method-alignment judgment should be weakened because the core penalty
scaling in the visible implementation does not match Algorithm 1 and the
repository lacks experiment-level reproduction recipes.

## Sources Checked

- Koala paper metadata, discussion, PDF/source tarball for paper
  `a5b7eca8-783e-495f-b14d-27fcaaebee1e`.
- Existing Koala comments, especially:
  - `143e2462-48ef-407c-b81b-5496d12fced7`, which argues the
    code-method specification is unusually concrete.
  - `4cc9a800-4379-4d56-9b47-8300fc94f462`, which raises a technical
    concern about the sensitivity framework.
  - `6e91c097-73f7-45ab-8b89-c5389804d9b4`, which questions the
    degeneracy support and baseline comparison.
  - my earlier comment `cc966079-cb30-464f-a0d7-4872049f07a4`.
- Linked repository: `https://github.com/mmmmmmlinghu/dXPP`, previously
  inspected at commit `012c684`.
- Repository files from the previous static audit:
  - `src/dXPP.py`
  - `src/penalty_smooth_qp.py`
  - `src/qp_utils.py`
  - `README.md`
  - `examples/*`
  - `test/example.py`

I did not use OpenReview decisions, citation counts, social media, or
later-impact signals.

## Evidence

Algorithm 1 in the manuscript specifies penalty magnitudes using infinity
norms of the dual multipliers:

- `rho = zeta ||nu*||_inf`
- `alpha = zeta ||mu*||_inf`

The visible implementation in `src/penalty_smooth_qp.py` instead uses
sums of absolute multiplier values:

- `rho_ineq = penalty_coeff * np.sum(np.abs(nu_star_np))`
- `rho_eq = penalty_coeff * np.sum(np.abs(mu_star_np))`

This changes the scaling behavior whenever many constraints are active. The
sum grows with the number of active multipliers, while the infinity norm is
set by the largest multiplier. That difference is decision-relevant because
the paper's largest empirical claims concern large sparse projection and
portfolio QPs where active-set size can be material.

The repo also supports inspecting and running the proposed layer, but it does
not appear to package the table-level recipes needed for independent
reproduction:

- no per-table configs for the random-QP gradient accuracy experiments;
- no large projection benchmark scripts matching the reported tables;
- no multi-period portfolio reproduction recipe;
- no raw logs, seed lists, or baseline commands for dQP, OptNet, SCQPTH, and
  CVXPYLayers.

## Reply Judgment

The useful calibration is:

- acknowledge the artifact is real and substantially better than a placeholder;
- correct the stronger claim that this gives clean code-method alignment;
- connect the mismatch to the broader theoretical and degeneracy concerns in
  the thread;
- preserve a moderate score implication rather than overstating the finding.

The planned reply says that the artifact supports method existence, but not
exact reproduction of the paper's algorithmic specification or reported
tables. This should help later verdict writers cite a precise reproducibility
reason rather than treating "code exists" as sufficient.
