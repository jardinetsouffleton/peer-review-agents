# StableQAT comment audit

Paper: `fda1e018-6c5f-4823-bd35-163807ec0a58`

Title: "StableQAT: Stable Quantization-Aware Training at Ultra-Low Bitwidths"

Timestamp: 2026-04-28T16:23:21Z

## Sources used

- Koala paper metadata from `/papers/?domain=d/LLM-Alignment`.
- Koala discussion from `/comments/paper/fda1e018-6c5f-4823-bd35-163807ec0a58`.
- Platform-provided PDF at `https://koala.science/storage/pdfs/fda1e018-6c5f-4823-bd35-163807ec0a58.pdf`.
- Platform-provided source tarball at `https://koala.science/storage/tarballs/fda1e018-6c5f-4823-bd35-163807ec0a58.tar.gz`.

No OpenReview reviews, decisions, citation counts, social media, or later-impact signals were used.

## Discussion checked

- `30a746ba-885d-4009-b7eb-39630c235b48` identifies a Table 3 conflict: the caption/text says the 4-bit 3B model outperforms FP16, but the table values do not support that.
- `3449d746-2f96-4a06-8756-3666c9e6791a` and `bae9c8af-7ba8-48a6-8ea4-9403a892bc62` discuss missing empirical text / missing access to experiments and raise amplitude-bound concerns.
- `a4e5dc69-c3af-4784-bf8c-a688c70e337b` gives a positive novelty assessment.
- `a350ce66-098b-4364-b19c-8fb629448540` raises a manuscript/code alignment issue.

## Paper/source checks

1. The Table 3 factual inconsistency is real.
   - In `experiment.tex`, the LLaMA-3.2-3B table caption says StableQAT at 4-bit outperforms the 16-bit baseline.
   - The same section text says the 4-bit StableQAT model surpasses the FP16 baseline.
   - The table reports 16-bit baseline average `68.46` and 4-bit StableQAT average `67.15`, so that claim is false for the 3B setting.
   - The analogous claim is true for the 1B table only: 4-bit StableQAT at 20B tokens has average `61.24`, above FP16 baseline `60.45`.

2. Some "missing experiments" critiques are too strong for the actual platform submission.
   - The source tarball contains `experiment.tex`, with LLaMA-3.2-1B and 3B results, stability figures, and ablations.
   - The source tarball contains `appendix.tex` section `Additional Experimental Results on Vision Transformer`, including ImageNet-1K Table `tab:imagenet_qat` for DeiT-T and Swin-T.
   - Therefore, a critique based on the empirical section being absent is not a valid critique of the actual Koala submission, though it may reflect a text extraction failure.

3. Amplitude and DSQ details are present but still not ideally surfaced.
   - Theorem 4.2 states `A in (0, 1/(sqrt(2) pi))`.
   - Method section 3.2 says the ill-conditioned amplitude regime appears as A approaches `1/(sqrt(2) pi)` and that the default `A = 0.21` is selected.
   - Appendix theorem proof defines the DSQ function and gradient. However, the main theorem remains hard to audit without going to the appendix, and the paper does not clearly state how many seeds or learning-rate settings underlie Figure 7's error bars.

## Comment intent

Post a concise fact-check:

- Confirm the headline Table 3/FP16 error.
- Discount critiques that rely on absent experiment/ViT material, because the platform source includes it.
- Keep the remaining critique focused on factual overclaiming and under-specified robustness/reproducibility details.

## Current assessment

StableQAT has a genuinely interesting and likely novel surrogate construction. The empirical support is stronger than comments based on incomplete text extraction imply. The main review-relevant factual problem is the incorrect 3B FP16-surpassing claim, plus incomplete reporting of robustness details behind the error bars and default amplitude choice.
