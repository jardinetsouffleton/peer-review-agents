# Morphology Policy Artifact Check

Paper: `7d2a0e82-0e30-4178-9b7a-3db772b01f2a`

Title: "Embedding Morphology into Transformers for Cross-Robot Policy Learning"

Agent: `repro-code-auditor`

Date: 2026-04-28

## Scope

I inspected the paper source bundle and the linked `sim-evals` repository:

- `https://github.com/arhanjain/sim-evals`
- cloned commit: `3a6b0e8`

The paper also links external simulator/dataset resources for Unitree and SO101, but the only repository I cloned for detailed inspection was `sim-evals`, because it is the DROID evaluation suite explicitly footnoted in the DROID experiment section.

## Paper Evidence

The paper's central method adds morphology-specific modules to the `pi0.5` action policy:

- kinematic tokens with temporal chunking;
- topology-aware attention masks/biases such as Full-Mask, Mix-Mask, and Soft-Mask;
- FiLM-based joint-attribute conditioning;
- auxiliary kinematic tokens in some ablations.

The paper reports many trained variants:

- DROID AP-FT from `pi05-base`, batch 32, horizon 16, 100k steps;
- Unitree G1 Dex1 Full-FT, batch 8, horizon 32, 60k steps;
- DROID+SO101 AP-FT, batch 32, horizon 16, 125k steps;
- 300 rollout trials per experimental condition, with Wilson 95% confidence intervals;
- success defined by an AABB target-region criterion plus dwell/stationarity requirements.

## Repository Evidence

The cloned `sim-evals` repository contains:

- `README.md` describing "DROID Sim Evaluation";
- `run_eval.py`, an example rollout script;
- a DROID websocket policy client in `src/sim_evals/inference/droid_jointpos.py`;
- IsaacLab environment code for DROID scenes.

I did not find:

- implementation of kinematic tokens, topology-aware attention masks, FiLM joint descriptors, auxiliary kinematic tokens, or pi0.5 training modifications;
- AP-FT or Full-FT training scripts for the paper's DROID, Unitree, or DROID+SO101 variants;
- config files mapping Table 1, Table 2, Figure 4, or the appendix ablations to exact model flags/checkpoints;
- manifests for the DROID 1/8 subset, Panda/SO101 8:2 mixture construction, seed lists for the 300 rollouts, or checkpoint paths for the reported models;
- result aggregation scripts producing success rates and Wilson CIs from rollouts.

The public DROID evaluator is also not sufficient by itself to regenerate the paper's reported success metrics. `run_eval.py` writes videos under `runs/...`, but it does not compute or save per-episode success/failure outcomes. `src/sim_evals/environments/droid_environment.py` defines only a timeout termination in `TerminationsCfg`; I did not find the AABB dwell/stationary success criterion described in the manuscript.

## Conclusion

The released links help identify public simulators and datasets, but they do not expose the proposed morphology-aware policy implementation or the experiment orchestration needed to reproduce the reported tables and curves. The paper is unusually detailed in reporting training settings and CI methodology, but the artifact surface currently supports qualitative DROID rollouts of an existing policy more than end-to-end reproduction of the paper's method.

My platform comment should therefore distinguish paper-level reproducibility details from artifact-level reproducibility: the paper gives useful hyperparameter anchors, while the linked code does not yet provide the method, metric computation, or table-generation pipeline.
