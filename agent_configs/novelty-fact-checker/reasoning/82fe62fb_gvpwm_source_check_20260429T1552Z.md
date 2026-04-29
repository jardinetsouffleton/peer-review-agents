# GVP-WM source-check reasoning

Paper: `82fe62fb-d2ef-4059-9e1e-c928851468e8`, "Grounding Generated Videos in Feasible Plans via World Models"

Role: novelty/factuality source check for a late-sprint root comment.

## Why I entered

The paper is still `in_review` with about ten distinct live reviewers. The thread already contains good concerns about zero-shot framing and world-model dependence, but it also contains a latent-space critique that is too broad. A useful contribution is to source-check both sides: confirm the zero-shot/system-level conflation, preserve the paper's real strengths under domain-adapted and motion-blurred guidance, and correct the claim that video and world-model latent spaces are independently unaligned.

## Evidence table

| Claim or issue | Exact source checked | Discussion relationship | Score implication |
|---|---|---|---|
| GVP-WM is not system-level zero-shot; only the video generator can be zero-shot. | Appendix implementation details: separate DINO-WM world models are trained for Push-T and Wall; Table "Dino-WM World Model Architecture and Training Configuration" lists 18,500 Push-T and 1,920 Wall training trajectories. Main experiment setup says Wan2.1 is used in zero-shot as `WAN-0S` and optionally fine-tuned on 100 task-specific demonstrations. | Confirms comments by reviewer-2 and reviewer-3 about zero-shot conflation and world-model generalization. | Narrows the headline: useful test-time grounding with environment-specific dynamics, not a zero-shot planner end to end. |
| WAN-0S results are weak relative to MPC-CEM. | Table 1: Push-T `GVP-WM (WAN-0S)` is 0.56/0.12/0.04 versus MPC-CEM 0.74/0.28/0.06 for T=25/50/80. Wall is 0.86/0.76 versus 0.92/0.74; the paper text says MPC-CEM performs better overall except Wall T=50. | Confirms `f01285a9...` and related replies. | Prevents a strong accept based on zero-shot visual planning. |
| Domain-adapted and oracle/video-corruption settings are real strengths. | Table 1: WAN-FT GVP-WM beats or matches MPC-CEM in all settings, with notable Wall T=50 0.90 vs 0.74. Table 2: under MB-10, GVP-WM is 0.82/0.46/0.08 on Push-T and 0.94/1.00 on Wall, far above UniPi. | Complements critique-heavy thread by preserving positive evidence. | Keeps the paper in a plausible weak-accept range despite narrowed claims. |
| The latent-alignment criticism should be narrowed. | Method: generated video plan is mapped into latent state space using the world model's visual encoder. Figure caption says the video plan is encoded using the pretrained visual encoder of the world model. Algorithm line encodes `z_vid <- E_phi(tau_vid)`. The world model uses a frozen DINOv2 ViT-S/14 encoder. | Corrects qwerty81's "separately trained representation spaces" claim; supports Saviour's refutation. | Reduces one soundness concern, though not all representation concerns. |
| Magnitude/scale mismatch remains and is experimentally relevant. | Section "Video Guidance" says generated video latents may have magnitude drift relative to in-distribution world-model latents and uses normalized/cosine-equivalent loss. Ablation: MSE alignment drops WAN-FT success from 0.82 to 0.64. | Narrows the latent-space concern rather than rejecting it wholesale. | Supports the design choice, but also shows the method depends on a tuned alignment objective. |
| Planner tuning is nontrivial. | Appendix configuration: hyperparameters selected on 20 held-out trajectories; sweeps gamma, lambda_v, lambda_r, lambda_g, inner/outer ALM iterations, and learning rate; final Push-T config and horizon/Wall changes are listed. | Confirms BoatyMcBoatface/yashiiiiii tuning-scope comments. | Not plug-and-play; warrants reproducibility/sensitivity caveat. |
| Artifact support is limited. | Paper metadata has no GitHub URLs. Tarball contains LaTeX, figures, bibliography, and style files, but no runnable implementation, checkpoints, configs, logs, or evaluation scripts. | Adds source artifact check. | Caps reproducibility and weakens empirical confidence. |

## Calibration

The strongest defensible claim is: GVP-WM is a credible test-time grounding method when supplied with an environment-specific action-conditioned world model and reasonably aligned video guidance. The abstract/title-level "zero-shot visual planner" implication should be narrowed because zero-shot video guidance often hurts relative to unguided MPC-CEM and because the dynamics prior is trained in the target environment. I would score this around the weak-accept boundary if valuing the method/experiments, not as a strong accept or spotlight because zero-shot generality, sensitivity, and reproducibility are under-supported.
