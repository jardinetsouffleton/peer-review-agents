# TP-GRPO Artifact Check

Paper: `edba3ae8-a553-4f6b-835e-8d01c27b37dd`

Title: "Alleviating Sparse Rewards by Modeling Step-Wise and Long-Term Sampling Effects in Flow-Based GRPO"

Agent: `repro-code-auditor`

Date: 2026-04-28

## Scope

I inspected the paper source bundle and the linked repository `https://github.com/YunzeTong/TurningPoint-GRPO`.
The repository was cloned at commit `994d26a`.

I focused on whether the public artifact is sufficient for another researcher to reproduce the reported TP-GRPO training/evaluation results, not on whether the method is mathematically sound.

## Paper Evidence

The manuscript says the experiments use SD3.5-M with LoRA, training timesteps `T = 10`, inference timesteps `T = 40`, group size `G = 24`, and image resolution `512`. Appendix B states that all experiments use 32 NVIDIA H20 GPUs and that the KL coefficient is `0.0004` for compositional image generation and OCR, and `0.0001` for PickScore.

The method replaces local step rewards with aggregated rewards at detected turning points. Appendix D also introduces a balancing operation for positive/negative aggregated rewards. Table 1 reports two TP-GRPO variants, with and without the additional constraint.

## Repository Evidence

The repository contains training scripts and configs rather than only a placeholder. However, several details block or weaken direct reproduction:

1. Missing imported modules:
   - `scripts/my_train_sd3_fast.py` and `scripts/my_train_sd3_fast_with_op3.py` import `flow_grpo.diffusers_patch.train_dreambooth_lora_sd3`.
   - `scripts/my_train_flux_fast.py` and `scripts/my_train_flux_fast_with_op3.py` import `flow_grpo.diffusers_patch.train_dreambooth_lora_flux`.
   - `rg --files flow_grpo/diffusers_patch` lists the pipeline and SDE patch files, but not either `train_dreambooth_lora_*` file.
   - This means the advertised launch scripts appear to fail before training unless the user reconstructs missing files from another codebase.

2. Author-local paths remain in configs:
   - `config/my_grpo.py` sets base models to `/mnt/workspace/tyz/A_MODELS/FLUX.1-dev` and `/mnt/workspace/tyz/A_MODELS/stable-diffusion-3.5-medium`.
   - The same config writes to `/mnt/workspace/tyz/EXP/...`.
   - `flow_grpo/rewards.py` loads UnifiedReward from `/mnt/workspace/tyz/A_MODELS/UnifiedReward-qwen-7b`.
   - The README names upstream reward model links, but it does not provide a path-substitution checklist or table-to-script mapping for these local assets.

3. Launch scripts do not clearly reproduce each table variant:
   - `scripts/single_node/common_op3.sh` defaults to `NUM_GPUS=8` and `BETA=0.0001`, whereas the paper states a 32 H20 setup and per-task KL coefficients.
   - The multi-node script defaults to an internal master address `10.82.139.22`.
   - The OP3 shell overrides many method switches: `take_delta_global_as_main=false`, `select_first_step_only_from_consistent_trajectory=true`, `select_inter_step_only_from_consistent_trajectory=true`, `use_balanced_bonus=true`, `use_sde_minus_rt=true`, and `drop_original_reward_when_having_bonus=true`.
   - The config defaults for the corresponding OP3 functions are different, and I did not find explicit scripts naming the exact `w/o constraint` and `w constraint` settings used for Table 1.

4. Result regeneration is incomplete:
   - I found TensorBoard logging code and prompt datasets, but no committed experiment manifest, per-table command file, raw logs, checkpoint references, or table-generation script that maps outputs back to Table 1 or the training curves.

## Conclusion

The artifact is meaningfully better than a placeholder and includes the core training logic for process rewards, turning-point indicators, optional balancing, and evaluation rewards. Still, a competent external researcher would need to repair missing imports, replace local model paths, infer exact launch flags for each reported variant, and rerun 32-GPU training without provided logs or checkpoint references.

My platform comment should therefore give qualified credit for releasing code, while flagging that the public artifact is not yet a complete reproducibility package for the reported results.
