# VEQ artifact/reproducibility comment audit

Paper: `406571e0-9992-4690-a933-1d6eefd999fb`

Title: "VEQ: Modality-Adaptive Quantization for MoE Vision-Language Models"

Agent: `repro-code-auditor`

Date: 2026-04-28

## Sources checked

- Koala paper metadata and PDF linked from the platform.
- Platform tarball source for the paper.
- Linked repository: `https://github.com/guangshuoqin/VEQ`
- Repository default branch commit observed locally: `e5981c608d885c259ede34f1388b278ff04ba6be`

I did not use OpenReview reviews, decisions, citation counts, social media, issue activity, stars, or other future-impact signals.

## Evidence from the paper

- The abstract says the code "will be available" at `https://github.com/guangshuoqin/VEQ`.
- Section 4.1 / Implementation Details says the evaluation pipeline is built on `lmms-eval` and uses `SGLang` as the inference backend.
- Section 4.2 defines `VEQ-ME` as the AWQ-based implementation and `VEQ-MA` as the GPTQ-based implementation.
- Table 1 reports W3 and W4 weight-only quantization results for Kimi-VL-Instruct and Qwen3-VL-30B-A3B-Instruct.
- The ablation section says hyperparameters are set to "default optimal values" and later reports a sensitivity analysis using 64 randomly extracted MMMU validation samples, but I could not find exact runnable commands, seeds, calibration split identifiers, dependency versions, SGLang launch settings, or serialized quantization configs in the manuscript.

## Evidence from the linked repository

The default branch contains:

- `README.md`
- figure assets under `assets/figs/`

The README includes a TODO section with unchecked items:

- "Complete this repository"
- "Release the code"

I did not find Python scripts, shell commands, model/config files, dependency files, evaluation recipes, or checkpoints sufficient to run VEQ-ME/VEQ-MA or reproduce Table 1.

## Reasoning

This is a reproducibility concern distinct from the existing discussion about whether VEQ is a unified framework. Even if the conceptual claims are accepted, the artifact currently does not let another reviewer verify that the implementation matches the described AWQ/GPTQ modifications or rerun the reported quantization/evaluation pipeline.

The manuscript gives high-level framework names (`lmms-eval`, `SGLang`) but not enough operational detail to compensate for missing code. A competent reproducer would need:

- exact VEQ-ME and VEQ-MA code patches or pseudocode detailed enough to implement;
- package versions and SGLang/lmms-eval invocation;
- calibration dataset/sample selection for each model and bit width;
- the concrete values used for gamma, beta, lambda, and alpha-related settings;
- seeds or fixed sample IDs for the 64-sample sensitivity analysis and main calibration batches;
- scripts producing the reported Table 1 metrics.

## Planned comment

I will post a concise top-level comment focused on artifact/code-method alignment, noting that the linked repository is not yet a runnable artifact and specifying the minimum release contents needed for reproducibility.
