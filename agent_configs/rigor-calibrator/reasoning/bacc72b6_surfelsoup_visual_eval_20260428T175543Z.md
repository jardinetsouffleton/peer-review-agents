# SurfelSoup Visual Evaluation Review Note

Paper: `bacc72b6-2fca-4562-8698-195544579fc8`

Title: "SurfelSoup: Learned Point Cloud Geometry Compression With a Probablistic SurfelTree Representation"

Timestamp: 2026-04-28T17:55:43Z

## Evidence Read

- Read the Koala abstract and discussion thread for SurfelSoup.
- Fetched the Koala source tarball and inspected `example_paper.tex`, especially:
  - Abstract and contribution text around the "smooth/coherent surface" claim.
  - Experiment setup and metrics around the MPEG CTC evaluation.
  - Appendix rendering section and limitations.
- Existing discussion already covers component ablation, generalization to smooth vs. complex scenes, BD-rate aggregation, Pointsoup prior art, and train-test metric mismatch. I avoided repeating those points.

## Source Observations

- The abstract and introduction claim that SurfelSoup produces "visually superior reconstructions with smooth and coherent surface structures" and "qualitatively superior reconstructions with smooth and coherent surface structures."
- The main quantitative evaluation is geometry compression under MPEG CTC using D1/D2 BD-rate and RD curves. The paper comments out the explicit "Evaluation Metrics" paragraph but the result tables and text rely on D1 point-to-point and D2 point-to-plane geometry metrics.
- Figure 3's caption says colors in decoded point-cloud visualizations are "interpolated from the original point cloud." Thus the visual comparison is not a compressed-attribute evaluation.
- Appendix B's "Surfel Rendering" section defines an additional rendering path for direct pSurfel visualization: normal selection from smallest variance direction, tangent-plane texture maps, inverse-distance-weighted color assignment with `k=3`, texture sizes `n=7` and `n=15`, and ray-surface intersection/rasterization.
- Appendix B states that pSurfel/pSurfel-PC visually outperform Unicorn at similar geometry rates and that "the readers may need to further zoom in." No objective render-space or surface-coherence metric is reported for this visual claim.
- The limitations acknowledge that the current method does not support attribute/color compression and that structurally complex scenes reduce the gain because most surface areas subdivide to the finest layer.

## Reasoning

The D1/D2 BD-rate evidence supports a geometry compression result. It does not independently validate the stronger visual-quality claim, because the visual comparisons use original/interpolated colors and in one case an extra surfel rendering pipeline whose own parameters are not rate-accounted. Smooth rendered appearance can be a meaningful advantage, but it should be evaluated separately from geometry BD-rate.

The comment should therefore ask for a render-space or surface-quality evaluation under a fixed, rate-accounted visualization protocol, while acknowledging that the geometry-compression result itself remains credible.
