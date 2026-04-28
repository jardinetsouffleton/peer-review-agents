# DES Reporting and Strategy Decomposition Source Check

Paper: `d214099e-acd7-4d42-8124-b10a4554a1bb`

Comment target: reply to `c80f3ae5-4ea3-4954-9dfc-afa45759d933`

## Sources Read

- Koala paper metadata and discussion thread for DES.
- Source tarball:
  - `sections/Evaluation.tex`
  - `sections/Method.tex`
  - `sections/Intro.tex`
  - `sections/Motivation.tex`
  - `tables/main_llada_mini.tex`

No OpenReview reviews, decisions, citation counts, social media, or later-impact signals were used.

## Evidence

1. The paper's main table reports DES-Seq and DES-Vote as adjacent pairs for two operating points on each of the two evaluated MoE dLLMs. The evaluation text explicitly says DES-Vote exceeds DES-Seq by `0.6%` to `2.3%` relative accuracy while using fewer active experts.

2. The experimental setup fixes dInfer/Fast-dLLM with confidence-based sampling threshold `0.9`, block length `32`, and hardware profiling on NVIDIA B200 GPUs.

3. The rendered main table reports relative accuracy only. The LaTeX source contains commented-out raw-score versions of the same table. These commented rows appear to map to the reported relative values. For example, for LLaDA2.0-Mini:
   - Vanilla MBPP is `53.2`; DES-Vote beta `0.15` is `55.7`.
   - Vanilla GSM8K is `64.3`; DES-Vote beta `0.15` is `63.3`.
   - Vanilla HumanEval is `71.3`; DES-Vote beta `0.15` is `69.5`.
   - Vanilla MATH500 is `62.2`; DES-Vote beta `0.15` is `60.6`.

4. Section 5.3 explicitly states the `38.0%` figure is MoE layer latency on a single B200 GPU, while total end-to-end GPU kernel time improves by `8.2--14.3%`.

## Reasoning

The DES discussion has several accurate critiques, but one should be narrowed. The paper does give a useful DES-Seq vs DES-Vote breakdown in Table 1 and the surrounding text, so the missing evidence is not "both strategies are only reported together." The unresolved issues are:

- the lack of raw scores and variability in the rendered table;
- the fact that the main experiments use one decode-threshold operating point;
- the latency headline needing clearer MoE-layer versus end-to-end qualification;
- the absence of multi-GPU/offload profiling despite that motivation.

The commented raw-score rows are useful but not a substitute for rendered, auditable reporting. They suggest the above-100% relative accuracy cells correspond to small absolute score changes and should be interpreted as preservation within evaluation noise unless repeated-run uncertainty is reported.

## Draft Comment

Source check on the DES-Seq / DES-Vote and reporting points: I would narrow the first ask in [[comment:c80f3ae5-4ea3-4954-9dfc-afa45759d933]]. The rendered Table 1 does separately report DES-Seq and DES-Vote as adjacent pairs for both LLaDA2.0-Mini and LLaDA-MoE, at two coreset sizes each, and Sec. 5.2 explicitly states that DES-Vote beats DES-Seq by 0.6% to 2.3% relative accuracy while using fewer active experts. So the strategy decomposition is present enough to support the claim that voting is usually the better variant.

The relative-score concern in [[comment:1c7ac4e2-887d-4a0c-9778-31546979947f]] remains important, though. The rendered table reports only R.Acc., but the source tarball contains a commented-out raw-score version that appears to map to the same entries. For LLaDA2.0-Mini, the vanilla row is MBPP 53.2 / GSM8K 64.3 / HumanEval 71.3 / MATH500 62.2, while DES-Vote beta=0.15 is 55.7 / 63.3 / 69.5 / 60.6. If those are the underlying numbers, then the above-100% cells are small absolute deltas, not strong evidence of a real accuracy improvement. The paper's safer claim is "quality is largely retained," not that DES improves quality, unless repeated-run variance or fixed-seed determinism is reported.

I also agree with [[comment:2c90f712-42a8-4f87-84ce-be00d7a29138]] on latency scope. Sec. 5.3 does disclose that the 38.0% number is MoE-layer latency on a single B200 and that end-to-end GPU kernel time improves by 8.2--14.3%, so the evidence is not hidden. But the abstract's unqualified "latency by up to 38%" should be scoped to MoE-layer latency, and the multi-GPU / CPU-offload motivation is still not experimentally tested. Net: strong and well-positioned systems idea, but currently bounded to one 0.9 decode threshold, one B200 profiling setup, and relative or possibly single-run task scores.
