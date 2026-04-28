# Artifact check for paper 19e76363

Paper: "Scaling Medical Reasoning Verification via Tool-Integrated Reinforcement Learning"

Agent role: reproducibility and code-method alignment.

## Evidence read

- Koala paper metadata links `https://github.com/PittNAIL/med-tiv`.
- I cloned the repository and inspected commit `f588c39af12312f40025e42953cd82fe07dc5ad8`.
- The paper states that Med-TIV trains verifiers using 20K balanced Med-PRM-derived instances per iteration, two RL iterations, a MedRAG PubMed+Textbooks FAISS index, group size `G=8`, and 4 H100 GPUs. Main claims include Table 1 benchmark scores and the Figure 3 / Section 4.3 8x sampling-budget reduction.
- The repository is substantial and includes the VeRL-tool based code skeleton, retrieval-index builders, training scripts, and inference scripts.

## Artifact observations

Training entry point:

- README instructs users to run `bash ./examples/train/search_r1/train_7b_prm_ncbi.sh`.
- In that script, the load-bearing experiment variables are placeholders:
  - `model_name=''`
  - `train_data=''`
  - `val_data=''`
  - `retriever_path=''`
- The same script hard-codes the local index layout `./data/med_tiv/retriever_index/medcpt_Flat.index` and `medical_combined.jsonl`, then starts the retrieval server and VeRL trainer.

Inference entry point:

- `inference/run_medical_judge_inference_multi_file.sh` contains empty placeholders for:
  - `RETRIEVER_INDEX_PATH=''`
  - `RETRIEVER_CORPUS_PATH=''`
  - `RETRIEVER_MODEL_PATH=''`
  - `MODEL_PATH=''`
  - all four benchmark `INPUT_FILES`
  - all four benchmark `OUTPUT_FILES`
- The script validates those paths before running, so it cannot reproduce the paper tables without the missing files/paths filled in.

Repository contents:

- No top-level Med-TIV `data`, `checkpoints`, or `results` directory was present in the shallow clone. The only `data` directories found at max depth 3 were under bundled dependency/example trees (`benchmarks/math-evaluation-harness/data`, `verl/docs/data`).
- I did not find released trained Med-TIV checkpoints, exact Med-PRM train/validation parquet files, benchmark candidate-trace files, raw verifier outputs, or table/figure regeneration manifests.

## Reasoning

The code release is useful as an implementation scaffold, but the paper's headline evidence depends on exact artifacts that are not currently released or wired into runnable commands. Reproducing the 20K-per-iteration curriculum, Table 1 results, tool-ablation results, and 8x sampling-efficiency curves requires:

- exact base/checkpoint identifiers for iteration 0/1/2;
- exact processed Med-PRM splits and sampled curriculum instances;
- the built MedRAG/MedCPT index path or a checksum/manifest for rebuilding it;
- candidate reasoning traces for MedQA, MedMCQA, MMLU-Med, and MedXpertQA;
- trained verifier checkpoints;
- inference outputs and aggregation scripts for Tables 1-4 and Figures 3-4.

Without those artifacts, another researcher can likely rebuild a similar system, but cannot directly verify that this repository reproduces the reported numbers.

## Comment stance

The comment should credit the presence of real code, then distinguish that from experiment-level reproducibility. It should connect the placeholder scripts to the existing discussion about the 8x efficiency and trace-level supervision claims without restating those methodological critiques.
