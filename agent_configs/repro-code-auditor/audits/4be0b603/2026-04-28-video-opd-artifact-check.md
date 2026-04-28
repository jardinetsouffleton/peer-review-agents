# Artifact check for paper 4be0b603

Paper: "Video-OPD: Efficient Post-Training of Multimodal Large Language Models for Temporal Video Grounding via On-Policy Distillation"

Agent role: reproducibility and code-method alignment.

## Evidence read

- Koala metadata links `https://github.com/TencentARC/TimeLens`.
- I cloned the repository and inspected commit `5d90c06`.
- The paper's method section defines Video-OPD as on-policy distillation:
  - sample trajectories from the current student policy;
  - evaluate each student token under a fixed teacher;
  - define dense token-level rewards from reverse KL;
  - update the policy with those token-level rewards;
  - use TVDF to filter/prioritize 2,500 samples via teacher reliability and teacher-student disagreement.
- The experiment section says the base model is Qwen3-VL-8B-Instruct, the teacher is Qwen3-VL-32B post-trained with GRPO, and GRPO uses 8 rollouts per instance.

## Repository observations

- The repository is a real TimeLens code/data/model release with evaluation scripts, dataset loaders, SFT scripts, and GRPO training scripts.
- `train_scripts/run_grpo_qwen3_8b.sh` calls `training/train/train_grpo_timelens.py` with `--reward_funcs tiou`, i.e. a standard temporal-IoU reward path.
- `train_scripts/run_grpo_and_eval_qwen3_8b.sh` requires an SFT checkpoint path and filtered JSONL path, then runs the GRPO script and evaluates the resulting checkpoint.
- `train_scripts/run_sft_qwen3_8b.sh` performs supervised fine-tuning, not Video-OPD.
- A source search for Video-OPD-specific identifiers and concepts (`video-opd`, `opd`, `TVDF`, `teacher`, `reverse KL`, `distill`) did not reveal a method implementation in the Python or shell code. The code paths visible in `training/trainer/grpo_trainer_qwenvl.py` are GRPO/reward-function paths adapted from TRL.

## Reasoning

The linked artifact supports TimeLens benchmark/model evaluation and GRPO/SFT training, but it does not appear to implement the ICML paper's central method. Reproducing the reported Video-OPD results would require:

- teacher model identifiers/checkpoints for the Qwen3-VL-32B-GRPO teacher;
- code for evaluating teacher log probabilities on student-generated trajectories;
- code for constructing per-token reverse-KL rewards/advantages;
- TVDF filtering code and manifests for the selected 2,500 training samples;
- exact comparison recipes for GRPO, OP-FKD, OP-RKD, and Video-OPD;
- raw logs/checkpoints for convergence-time, convergence-step, cost, and multi-round ablations.

The public repo may be useful for reproducing TimeLens evaluation, but not for independently checking the Video-OPD training mechanism or the efficiency claims in the ICML submission.

## Comment stance

The comment should be balanced: credit the real TimeLens release, then state that the linked artifact is not aligned with the paper's Video-OPD method. Avoid using repo reputation or later public status as evidence; focus only on code-method alignment.
