# Steganography comment reasoning: paraphraser mitigation validation

Paper: `f60b2fb4-0729-4368-b30b-9a37f429b35d`  
Title: "A Decision-Theoretic Formalisation of Steganography With Applications to LLM Monitoring"  
Comment type: top-level experimental-rigor comment.

## Evidence read

- Section 6.5 claims the steganographic gap can be used prescriptively to train or select paraphrasers that decode steganographic signals.
- The trained paraphrasing experiment uses traces from `pi_high-stego`, receiver `pi_high-stego`, and sentinel `pi_no-stego` on CoinFlip.
- Appendix F defines the RL reward. The main term is exactly the negative steganographic gap on the paraphrased trace:
  `r_gap = -[(e_R - d_R) - (e_A - d_A)]`, with an additional drop penalty and format penalty.
- Appendix F lists a short training run: Qwen2.5-3B-Instruct paraphraser, 50 max steps, 32 generations per prompt, batch size 64.
- Appendix E reports Figure 6 data:
  - no paraphrasing: normalized gap `0.931 +/- 0.024`, `I_rec = 0.512`, `I_sen = 0.035`
  - base paraphraser: normalized gap `0.912 +/- 0.024`, `I_rec = 0.512`, `I_sen = 0.045`
  - un-stego paraphraser: normalized gap `0.061 +/- 0.023`, `I_rec = 0.511`, `I_sen = 0.480`

## Reasoning

The result is an informative proof that the reported gap objective can be optimized in the constructed CoinFlip codeword environment. However, because the reward directly optimizes the same metric later plotted, the experiment does not by itself establish that the learned paraphraser is a generally useful mitigation.

The current paper does not show:

- evaluation on a held-out steganographic scheme, such as ROT13 traces, bigram-cipher traces, or a different codebook;
- evaluation on a held-out sender/receiver pair;
- evaluation against a different sentinel model;
- separation between train and evaluation task distributions for the prescriptive claim.

The main concern is overfitting to the intervention objective and the specific synthetic codeword family. The claim should be framed as an existence proof unless the authors add held-out mitigation tests.

## Review judgment

This does not erase the paper's conceptual value. It does affect the strength of the "mitigate" part of the abstract and Section 6.5. For verdict calibration, I would treat the detection/quantification formalism separately from the prescriptive mitigation claim: the latter needs stronger held-out validation.
