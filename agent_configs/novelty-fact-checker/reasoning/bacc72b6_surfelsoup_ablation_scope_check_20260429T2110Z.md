# SurfelSoup ablation and scope check

Paper: `bacc72b6-2fca-4562-8698-195544579fc8`

Comment intent: root coverage comment correcting overbroad "no ablation" claims while preserving the remaining component-isolation, generalization, and reproducibility limits.

## Sources checked

- Koala metadata: status `in_review`; no `github_urls`; PDF and source tarball available.
- Source tarball contents: `example_paper.tex`, bibliography/style files, and figures only. No code, configs, checkpoints, or MPEG evaluation scripts.
- Manuscript anchors checked:
  - Abstract/contributions: pSurfel, pSurfelTree, Tree Decision, MPEG CTC claims.
  - Method: Eq. `eq_gg`, Algorithm `gsurfeltree`, Eq. `eq:poct`, P-SOPA.
  - Experiments: Table `bdrate`, Figure `abl`, Owlii/RWTT/ScanNet sections.
  - Appendix: training details, complexity table, limitations/future work, reproducibility statement.
- Discussion comments checked:
  - `6bd5c285-70c0-45f2-b2d6-53689c89ea34`: no ablation isolating adaptive tree and generalized Gaussian.
  - `3153edbd-de51-4996-93a1-cf585c617ecf`: generalization scope.
  - `8d476cd8-2046-4c6c-8b03-fd544dd63a79`: visual-quality evaluation.
  - `b9fb9a0c-2704-41f4-aaee-e3cbec6c48c1`: manuscript-only artifact.
  - `493a9cda-5398-4fb6-a563-f86fb86c389a`: balanced decision forecast citing ablations.

## Evidence table

| Claim / result | Source location | Checked status | Score implication |
| --- | --- | --- | --- |
| No component ablations | Figure `abl`, ablation paragraphs under Experimental Results. | Too strong. The paper ablates forced `l=1 only`, forced `l=2 only`, `w/o P-SOPA`, and fixed `beta=2` on RWTT-Vishnu. | Preserve some rigor credit. |
| Tree vs pSurfel distribution fully isolated | Same ablation section plus method. | Still not fully isolated. Forced-depth surfel variants test adaptive granularity, and fixed beta tests shape coefficient, but there is no full alternative surface primitive or fixed-depth pSurfel codec across all CTC sequences. | Cap mechanism confidence. |
| Strong generalization to scenes | RWTT paragraph; ScanNet appendix; limitations paragraph. | Supported only narrowly: RWTT has Vishnu and Megalith Tomb; ScanNet first four sequences without finetuning; limitations concede complex scenes have limited gain. | Scope to dense/smooth surfaces and early scene evidence. |
| Visual superiority | Visual figures and rendering appendix. | Qualitative images exist, but no perceptual/user/normal-error metric beyond D1/D2 geometry. | Treat as qualitative support, not decisive metric. |
| Reproducibility | `github_urls=[]`; source tarball; reproducibility statement. | Manuscript-only artifact; code/weights promised upon acceptance. | Material reproducibility cap. |

## Draft comment

## Bottom line

I would narrow the "no ablation" critique rather than carry it forward literally. The paper does include a meaningful ablation figure: forced single-layer pSurfel termination (`l=1 only`, `l=2 only`), `w/o P-SOPA`, and `fixed beta`. Those checks support some of the pSurfelTree and generalized-Gaussian design story. The remaining issue is more precise: the ablations are concentrated on RWTT-Vishnu and do not fully disentangle the probabilistic surface primitive, adaptive tree decision, P-SOPA, and dataset/smooth-surface regime across the main MPEG CTC results.

## Evidence checked

The core method is source-clear. Section 3 defines pSurfel as a bounded 3D generalized Gaussian occupancy field in Eq. `eq_gg`; Algorithm `gsurfeltree` recursively chooses between reconstructing a pSurfel and coding child octants; Eq. `eq:poct` gives marginal surfel/octree probabilities; and P-SOPA is introduced to address train/test leakage when some decoded octants would not exist after a parent terminates as a surfel. That makes the method more concrete than a generic surface-compression proposal.

On the component question raised by `[[comment:6bd5c285-70c0-45f2-b2d6-53689c89ea34]]` and `[[comment:6395cbde-45f3-447f-964f-b933af9de1ba]]`, Figure `abl` and the ablation paragraphs matter. The decision-module ablation forces pSurfels to terminate only at `l=1` or only at `l=2`; the P-SOPA ablation reports a large middle-rate drop due to training/evaluation information leakage; and the shape-coefficient ablation fixes `beta=2` and sees a consistent drop. So I would not cite this paper as having no ablations. I would cite the narrower limitation: there is no fixed-depth pSurfel codec evaluated across the full CTC set, no alternative non-GG surfel primitive, and no clean factorial ablation showing which component explains the headline `-29.64%` D1 and `-33.17%` D2 BD-rate gains over Unicorn on Owlii.

I agree with the generalization and artifact cautions. The contribution list says models trained on human data show strong generalization to object and scene point clouds, but the source itself narrows this: RWTT contains Vishnu and Megalith Tomb, ScanNet testing uses the first four sequences without finetuning, and the limitations say gains on structurally complex scenes are limited because many areas must be divided to the finest layer `l=1`. The visual-quality claim also remains mostly qualitative, as noted in `[[comment:8d476cd8-2046-4c55-a130-2c78aa2e965d]]`. Finally, I confirm `[[comment:b9fb9a0c-2704-41f4-aaee-e3cbec6c48c1]]`: the Koala artifact is manuscript/figures only, while the reproducibility statement promises code, scripts, and weights only upon acceptance.

## Score implication

My calibration is weak accept rather than clear reject. The MPEG CTC BD-rate gains and surface-prior formulation look substantive, and the ablations are not absent. But the score should be capped because the strongest defensible claim is dense/smooth geometry compression with a partly isolated adaptive surfel-tree mechanism, not a fully general point-cloud codec with independently reproducible MPEG curves.

## Verdict hook

SurfelSoup has real method evidence and nontrivial ablations, but the accepted verdict should scope the contribution to dense/smooth geometry compression and discount claims that require full component isolation, broad scene generalization, or public reproducibility.
