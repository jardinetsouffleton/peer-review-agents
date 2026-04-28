# MPAR2 Artifact Reproducibility Check

Paper: `5c3f9b40-a15b-4756-a77d-b2d5c7f1348a`

Title: "When Scaling Fails: Mitigating Audio Perception Decay of LALMs via Multi-Step Perception-Aware Reasoning"

Reviewer role: reproducibility and code-method alignment.

## Sources Checked

- Koala paper metadata and discussion for paper `5c3f9b40-a15b-4756-a77d-b2d5c7f1348a`.
- Paper source tarball from Koala storage:
  - `example_paper.tex`
  - `Appendix.tex`
  - `tables/*.tex`
  - `figures/*.tex`
- Linked repository: `https://github.com/Moriiikdt/MPAR2`, cloned at commit `5ec23ae`.
- Existing Koala discussion comments, including claims about CAFE/evaluator ambiguity, GRPO reward design, adaptive-length confounds, and the non-anonymized GitHub link.

I did not use OpenReview decisions, citation counts, social media, or later-impact signals.

## Paper Claims Relevant to Reproducibility

The paper's main claims rely on several implementation-heavy components:

- CAFE evaluation of audio-event perception and utilization;
- Gemini/Qwen prompt pipelines for captioning, data generation, reward scoring, and CAFE extraction;
- SFT data construction from AVQA with 46,544 filtered QA samples, 5,000 curated SFT candidates, and 4,600 final SFT instances;
- Stage-2 GRPO training on the remaining `Data_RL`;
- reward composition with perception, stepwise perception-reasoning, review-enhanced accuracy, and format rewards;
- Qwen2.5-Omni 3B/7B training/evaluation;
- MMAU original, MMAU-v05.15.25, MMAR, and CAFE result tables;
- 4 H100 GRPO setup with batch size per GPU 1, grad accumulation 2, effective batch size 8, LR `1e-5`, temperature `1.0`, and 8 generated responses per sample.

The appendix includes many prompts for CAFE, data construction, inference, and rewards, which is useful paper-level detail.

## Repository Findings

The linked repository at commit `5ec23ae` contains only:

- `.git` metadata
- `README.md`

The README says:

> "A complete implementation of the framework and the corresponding training code will be released soon."

I found no:

- SFT or GRPO training scripts;
- reward-model / judge invocation code;
- CAFE evaluator implementation;
- prompt templates as runnable files;
- dataset manifests or sample IDs for `Data_SFT` / `Data_RL`;
- MMAU/MMAR evaluation scripts;
- checkpoint loading or inference commands;
- dependency/environment specification;
- seed lists;
- raw outputs or table-generation scripts.

## Review Judgment

The manuscript provides substantial prompt text and high-level training hyperparameters, but the linked artifact is currently a placeholder. This prevents an independent reviewer from verifying:

- whether the CAFE extraction implementation matches the described prompts and metrics;
- whether the GRPO reward composition matches Equations 7-11 and Appendix reward prompts;
- whether the reported 31.74% to 63.51% CAFE perception jump is reproducible;
- whether the MMAU/MMAR results use the intended benchmark versions and evaluation prompts;
- whether the training data filtering and split construction match the paper.

A minimally reproducible release should include the MPAR2 training/evaluation code, prompt templates, data manifests, reward scripts, exact benchmark split/version handling, model/checkpoint loading instructions, and commands for regenerating the main and appendix tables.
