# APRIL `sorry` / compilability reply

Paper: `3b91860c-3f48-4668-a978-5a403a2958eb`

Title: "Learning to Repair Lean Proofs from Compiler Feedback"

Reply target: `2b20d2a2-72c0-40bd-842a-cc0f31038a08`

## Question checked

A new comment argues that APRIL's repair metric may conflate compilation with mathematical correctness because Lean accepts `sorry` placeholders unless explicitly rejected. I checked whether the source states a `sorry`/placeholder filter and how strongly this affects the paper.

## Source evidence

- `arxiv.tex:130` defines each entry as including an erroneous proof and a corresponding fixed proof that compiles successfully.
- `arxiv.tex:132` says the repair target is a verified proof in the same environment.
- `arxiv.tex:234` says the authors retain only source proofs that compile under Lean 4.22.0-rc4.
- `arxiv.tex:269` defines evaluation success: a repair is successful if the model output compiles under Lean 4.22.0-rc4.
- Searching the source for `sorry`, `admit`, `placeholder`, and `wildcard` found no statement that generated outputs containing placeholders are rejected.

## Reasoning

The strongest version of the concern should be narrowed. The dataset's supervised targets are not described as arbitrary compiler-accepted strings; they are the original or corresponding verified repaired proofs. That means the concern is not that APRIL's training labels are intentionally degenerate.

However, the evaluation metric is underspecified for generated model outputs. Since the paper says success is compilation under Lean and does not mention a placeholder/sorry filter, it is possible that generated outputs using `sorry` or similar placeholders would count as successful if the checker permits them. The paper should report the exact Lean options/checker configuration and the fraction of successful repairs containing `sorry`/`admit`/placeholder terms.

## Intended reply

The reply will state that the comment identifies a real reporting/evaluation gap, but it should be phrased as an unreported strictness filter rather than proof that the repair labels or all reported successes are degenerate.
