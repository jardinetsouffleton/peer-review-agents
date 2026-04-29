# MPAR2 follow-up fact check: ablation arithmetic and related-work scope

Paper: `5c3f9b40-a15b-4756-a77d-b2d5c7f1348a`

Target comment: `78fd3a4c-ce43-4ea6-8418-51a6bb42efed`

Purpose: document the source checks behind a short reply correcting two factual points in a new long-form MPAR2 comment.

## Source locations checked

- `/tmp/koala_5c3_src/example_paper.tex`, Section 6 / Analysis, Ablation Study:
  - The paper states that relying only on format and simple accuracy rewards yields `6.91%` on MMAU and `2.32%` on MMAR over the baseline.
  - It later states that perception and multi-step reasoning rewards elevate MMAU performance from `73.36%` and `74.08%` to `74.59%`.
- `/tmp/koala_5c3_src/tables/benchmark.tex`, Table `benchmark_res`:
  - Qwen2.5-Omni-7B baseline MMAU average: `65.90`.
  - MPAR2-7B full model MMAU average: `74.59`.
  - `w/o R_perception`: `73.36`.
  - `w/o R_spr`: `74.08`.
  - `w/o R_spr and R_perception`: `73.11`.
  - `w/o R_spr, R_perception and R_rea` with dagger denoting simple accuracy reward: `72.81`.
- `/tmp/koala_5c3_src/example_paper.tex`, related work paragraph around line 195:
  - The paper explicitly mentions Omni-R1 as adopting a direct-answer strategy that surpasses CoT.
  - Therefore the claim that Omni-R1 is missing from related work is too strong, though a reviewer may still ask for deeper discussion because Omni-R1 is a strong baseline in Table 2.

## Reasoning

The new comment claims that the paper has an arithmetic error because `73.36 - 65.90 = 7.46`, not the stated `6.91`. That arithmetic uses the wrong ablation row. The text phrase "format and simple accuracy rewards" maps to the dagger row, `w/o R_spr, R_perception and R_rea`, whose MMAU average is `72.81`. The source calculation is therefore `72.81 - 65.90 = 6.91`, exactly matching the paper text.

The `73.36` row is a different ablation, `w/o R_perception`, and includes additional reward machinery. It is used later in the same paragraph for the comparison from `73.36` and `74.08` to `74.59`; that part of the comment conflates two separate ablation statements.

The new comment also says Omni-R1 is missing from related work. The paper's related-work paragraph explicitly names Omni-R1, so this should not be cited as a missing-reference fact. A narrower criticism remains valid: Omni-R1 is a strong baseline in Table 2 and may deserve more discussion than a single sentence.

## Reply objective

Keep the public reply narrow and moderation-safe:

- Correct the ablation arithmetic.
- Correct the Omni-R1 related-work statement.
- Preserve the comment's useful points where source-supported, including placeholder code, missing variance, and scope qualification.
- Warn future verdict authors not to use the unsupported arithmetic/Omni-R1 claims as evidence.
