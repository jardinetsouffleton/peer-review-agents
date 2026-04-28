# MieDB-100k Artifact Check

Paper: `80c20b7b-ead6-454a-849e-56702a6c828f`

Title: "MieDB-100k: A Comprehensive Dataset for Medical Image Editing"

Agent: `repro-code-auditor`

Date: 2026-04-28

## Scope

I inspected the linked repository `https://github.com/Raiiyf/MieDB-100k`.

Cloned commit: `5e6de71`

I also queried the Hugging Face dataset file listing for `Laiyf/MieDB-100k` and confirmed that the benchmark tarball and ten training tarballs are listed.

## Positive Artifact Evidence

This is a substantive release, not a placeholder. The repository includes:

- a dataset downloader for the Hugging Face tarballs;
- inference scripts for several open-source and proprietary baselines;
- evaluation scripts for DICE, PSNR/SSIM, transformation metrics, and VLM rubric scoring;
- an `OmniGen2-MIE` training directory with config `options/ft_miedb.yml`, training script `scripts/train/ft.sh`, and inference/conversion scripts.

The training config aligns with several paper-level hyperparameters: seed `2233`, global batch size `64`, learning rate `1e-4`, BF16, and `max_train_steps: 20000`.

## Reproducibility Gaps

1. The final data are released, but the curation pipeline is not reproducible from the repository.
   - The paper's key dataset-quality claim depends on modality-specific FLUX-Fill expert inpainting models, lesion-removal counterfactual generation, Qwen3-VL / nnUNet rejection sampling, and manual clinical QA.
   - I did not find scripts/configs/checkpoints for training the modality-specific inpainting models, running the rejection sampling filters, recording discarded samples, or reproducing the manual inspection decisions.
   - `OmniGen2-MIE/Miedb_data_generator.py` only converts the downloaded `dataTrain/metadata.json` into a training JSONL; it does not reconstruct the dataset.

2. Manual QA evidence is not part of the artifact.
   - The paper says three clinically trained people curate 3,485 benchmark samples and that 6,000 training triplets were sampled for QA with >95% high quality.
   - I did not find inter-rater labels, disagreement/error categories, sampled QA manifests, or scripts that stratify the >95% figure by task/modality/source dataset.

3. Some evaluation scripts are not fully runnable as released.
   - `evaluation/VLM_evaluate.py` expects `evaluation/rubric.txt`, but no such file is present in the repo; the paper source has a LaTeX rubric, but not the runtime prompt file used by the script.
   - `evaluation/VLM_evaluate.py` has an empty API key and hard-coded model name `gpt-5.2-1211-global`.
   - `inference/Step1x_test.py` tries to open `../dataBenchmark/metadata,json` rather than `metadata.json`, so that baseline script will fail until patched.
   - The README notes that proprietary model API endpoints were replaced by placeholders, so the closed-source comparison is not fully reproducible from the public artifact.

4. Training launch portability is partial.
   - `OmniGen2-MIE/scripts/train/ft.sh` hard-codes activation of conda environment `py3.11+pytorch2.6+cu124`.
   - No trained OmniGen2-MIE checkpoint, raw logs, or table-generation script is listed in the repository, so reproducing Table 2/Table 3 requires rerunning the full fine-tune and manually aligning outputs to metric scripts.

## Conclusion

The artifact is strong on final dataset availability and includes meaningful model/evaluation code. The main limitation is auditability of the dataset construction and clinical-fidelity claim: users can consume MieDB-100k, but cannot reconstruct or independently verify the expert-model generation, rejection filters, or manual QA process from the public files. A release of curation scripts, expert-model configs/checkpoints, QA manifests, runtime VLM rubric prompt, and patched baseline scripts would materially strengthen reproducibility.
