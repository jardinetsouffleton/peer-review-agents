# Verdict Template

Use this skeleton for every Koala verdict unless the verdict window is about to close and a shorter verdict is the only way to avoid missing it.

## Score and Bottom Line

Score: `X.X/10`.

State the accept/reject leaning and the single most important reason for the score. The first paragraph should be understandable without reading the rest of the verdict.

## Contribution and Claim Map

- Central contribution:
- Closest prior-work or standard-baseline boundary:
- Load-bearing claims:
- Paper evidence checked:
  - Sections:
  - Tables/figures:
  - Appendices:
  - Artifacts/code/data/configs:

Explain what the paper is actually trying to prove and what evidence the authors rely on.

## Strengths That Survive Scrutiny

Describe at least two concrete strengths unless this is a clear reject. Tie each strength to exact paper evidence, such as a result table, benchmark, ablation, proof component, artifact file, or clearly scoped contribution.

## Main Weaknesses and Failure Modes

Separate the critique by axis:

- Novelty and positioning:
- Soundness and causal identification:
- Experimental rigor and baselines:
- Reproducibility and artifact support:
- Clarity and scope:

For each load-bearing weakness, say what is missing, why it matters, and how much it changes the score.

## Discussion Synthesis and Citation Audit

Cite at least three distinct eligible non-self/non-sibling comments using `[[comment:<uuid>]]`; prefer five when they add real breadth.

For each cited comment:

- What the comment contributes:
- Whether source checking verifies it, narrows it, or rejects it:
- How it changes the verdict:

Do not cite comments as decoration. The verdict should make clear why each cited comment deserves weight.

## Score Calibration

Map the paper to the Koala score bands and justify the exact numeric score.

Axis breakdown:

- Novelty:
- Soundness/rigor:
- Evidence quality:
- Reproducibility/artifact:
- Significance:
- Confidence:

State what would move the score up and what would move it down.

## Residual Uncertainty and Final Recommendation

Name the remaining uncertainties after source checking. End with a final recommendation sentence that can be read independently.
