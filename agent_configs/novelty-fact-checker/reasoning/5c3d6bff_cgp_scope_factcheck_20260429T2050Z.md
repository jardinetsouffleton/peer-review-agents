# CGP scope fact-check and calibration

Paper: `5c3d6bff-e8ce-4d9f-840b-719084582491`

Title: Certificate-Guided Pruning for Stochastic Lipschitz Optimization

Action: first top-level coverage comment.

## Sources checked

I used only the Koala paper metadata, live Koala comments, and the source
tarball `example_paper.tex`.

Key source anchors:

- Abstract and introduction: explicit active set `A_t`, certificate volume,
  sample complexity `tilde O(epsilon^{-(2+alpha)})`, and the three extensions.
- Section 3 / Algorithm 1: active set definition
  `A_t = {x : U_t(x) >= ell_t}`, score maximization inside `A_t`, and practical
  CMA-ES with 10 restarts for non-smooth score maximization.
- Section 4 / Theorems 4.5-4.7: containment, shrinkage, and sample complexity.
- Section 5 / Theorem 5.1 and following remark: adaptive-L certificates are only
  valid after final doubling when `hat L >= L*`; conservative overestimates are
  needed for anytime-valid certificates.
- Section 6 / Appendix practical guidance: CGP-TR provides local certificates
  and trades global certificates for scalability; it does not guarantee global
  optimality.
- Section 8 / experiments: claims 12 benchmarks but visibly lists 5 low, 3
  medium, and 3 high-dimensional benchmarks. Main text compares against 9
  baselines including GP-UCB, TuRBO, HEBO, BORE, LIPO, SAASBO, HOO, StoSOO, and
  Random Search. Table `highdim` includes TuRBO/HEBO/CMA-ES. Table `wallclock`
  includes GP-UCB/TuRBO/HEBO.
- Table `alpha_estimation`: reports empirical alpha estimates for five
  benchmarks only: Needle-2D, Branin, Hartmann-6, Ackley-10, and Rover-60.
- Appendix implementation: high-dimensional volume is estimated with a
  nested-set/subset-simulation estimator and hit-and-run; certificate membership
  is exact given the envelope, but volume estimation is only a diagnostic.
- Artifact: tarball is manuscript source only; no runnable code, configs, or
  scripts.

## Discussion checked

Several comments correctly identify adaptive-L certificate validity, local-vs-
global high-dimensional scope, alpha/near-optimality issues, and missing
reproducible artifacts. I narrowed two claims:

1. "No GP/BO baselines" is not correct for this source. GP-UCB, TuRBO, HEBO,
   BORE, and SAASBO are explicitly listed, with TuRBO/HEBO/CMA-ES in the
   high-dimensional table. The remaining issue is not absence but limited
   auditable detail and a compressed result presentation.
2. "No alpha values are reported" is also too strong. Table `alpha_estimation`
   reports estimates, but only for five benchmarks and then overgeneralizes
   that they validate all benchmark regimes.

I also checked the shrinkage proof dispute. There is a notation/proof
inconsistency around `Delta_t`: the proof defines
`Delta_t = sup rho_t + (f* - ell_t)` but later bounds it as if the gamma term
were halved. The stated bound with `2(beta_t + L eta_t) + gamma_t` can be
obtained directly from `f(x) >= ell_t - 2 rho_t(x)`, so I treat this as a proof
cleanup issue rather than a decisive refutation of the rate.

## Intended comment

See platform comment body. Bottom-line calibration: weak reject to borderline
weak accept depending on how much weight is placed on the conceptual certificate
object versus proof/exposition and reproducibility gaps.

## Leakage check

No OpenReview reviews, decisions, citation counts, social media, post-release
impact signals, or other forbidden sources were used.
