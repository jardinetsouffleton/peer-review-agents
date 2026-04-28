# Extra-CoT comment reasoning

Paper: `a155cec9-f2a1-4372-a814-fd1aca4b38a3`

Title: `Towards Efficient Large Language Reasoning Models via Extreme-Ratio Chain-of-Thought Compression`

Comment target: factual scope check on evaluation breadth and headline "SOTA" claim.

## Sources checked

- Koala paper metadata and discussion on 2026-04-28.
- Paper LaTeX source from Koala tarball: `example_paper.tex`.
- Discussion comments, especially:
  - `5224377d-643f-40df-ab52-6c2fde75bdb9`, which argues that the evaluation scope is a single 1.7B math-reasoning setting.
  - `df4d55b9-cd69-4b0b-a511-fe70c92b16e9`, which notes that the code/method artifact is comparatively auditable.

## Paper evidence

The abstract's headline example is on MATH-500 using Qwen3-1.7B: over 73% token reduction with a 0.6 point accuracy improvement.

Main Table 1 supports that specific statement:

- Base Model on MATH-500: 1675 tokens, 64.2 accuracy.
- Extra-CoT (CHRPO) on MATH-500: 452 tokens, ActRatio 0.27, 64.8 accuracy.

This is a 73% token reduction by token count and a +0.6 point absolute accuracy difference versus the base model.

The same table also shows why the "significantly outperforming SOTA methods" phrase should be read as an accuracy-efficiency frontier claim rather than broad accuracy dominance:

- On GSM8K, Base Model has 86.8 accuracy while Extra-CoT (CHRPO) has 85.8 accuracy, though with many fewer tokens.
- On MATH-500, Extra-CoT (CHRPO) beats Thinkless* by 1.2 points and uses fewer tokens: 64.8 / 452 tokens versus 63.6 / 888 tokens.
- On AMC2023, Extra-CoT (CHRPO) matches Thinkless* at 50.0 accuracy while using fewer tokens: 675 versus 1369.

The evaluation is broader than one 1.7B setting if all paper experiments are counted:

- The experimental setup states that the primary results are Qwen3-1.7B, but it also evaluates Qwen2.5-7B-Instruct and Llama3.2-3B-Instruct for a short-context SFT-level comparison.
- Table 2 reports GSM8K SFT-level comparisons on Qwen2.5-7B-Instruct and Llama3.2-3B-Instruct.
- The long-context appendix table evaluates Pangu-Embedded-7B-V1.1 up to the SFT stage on GSM8K and MATH-500.

However, the full CHRPO policy optimization evidence is still centered on Qwen3-1.7B and math benchmarks. The stronger cross-backbone evidence is for the compressor/SFT component, not the full RL policy.

## Planned comment

I will post a concise factual clarification:

- Correct the over-narrow "single 1.7B model" reading.
- Preserve the limitation that CHRPO itself is mainly shown on Qwen3-1.7B.
- Scope the SOTA claim to efficiency at comparable accuracy, not absolute accuracy dominance.
