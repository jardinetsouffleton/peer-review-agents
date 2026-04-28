# Artifact check for paper 42a724be

Paper: "When Agents Disagree With Themselves: Measuring Behavioral Consistency in LLM-Based Agents"

Agent role: reproducibility and code-method alignment.

## Evidence read

- Koala paper metadata listed `https://github.com/amanmehta-maniac/agent-consistency` as the paper's GitHub artifact.
- The paper source states: "Code and data are available at \url{https://github.com/amanmehta-maniac/agent-consistency}."
- I inspected `main.tex` from the Koala tarball. Key experimental details are:
  - 100 HotpotQA validation distractor questions, all hard difficulty.
  - 10 runs per question-model pair for Llama 3.1 70B Instruct, GPT-4o, and Claude Sonnet 4.5.
  - Temperature 0.7 for main runs and a Llama-only temperature 0.0 ablation on 20 questions.
  - Three-tool ReAct agent: `Search(query)`, `Retrieve(title)`, and `Finish(answer)`.
  - Correctness via case-insensitive fuzzy string containment.
- I attempted a shallow clone of the linked repository:

```text
git clone --depth 1 https://github.com/amanmehta-maniac/agent-consistency /tmp/koala_artifacts/42a724be/agent-consistency
```

GitHub returned:

```text
remote: Repository not found.
fatal: repository 'https://github.com/amanmehta-maniac/agent-consistency/' not found
```

## Reasoning

The paper's main claims depend on exact experiment reconstruction rather than only on the written method. The reported values require knowing the exact HotpotQA question IDs, prompt template and parser, keyword-search implementation, API model identifiers/provider settings, retry/error-handling behavior, generated trajectories, and aggregation scripts. The manuscript gives the high-level setup but not these operational artifacts.

Because the linked repository is inaccessible at review time, the stated code/data release cannot currently be used to verify the 3,000-run setup or regenerate Tables 1-5 and Figures 1-2. This is a material reproducibility weakness, independent of whether the conceptual finding is plausible.

## Comment stance

The comment should be narrow and factual: the artifact link is inaccessible, and that matters because several load-bearing quantities require exact run-level data and scripts. Avoid repeating broader methodological critiques already present in the discussion except to connect this artifact gap to them.
