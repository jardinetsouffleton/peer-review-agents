# Offline Autoresearch Loop

This directory contains seed tasks and prompt variants for iterating on Koala
reviewer agents before launching them against the live platform.

The loop is intentionally offline:

- It does not call Koala.
- It does not post comments or verdicts.
- It scores draft outputs with process-quality proxies: paper grounding,
  specificity, rubric coverage, citation readiness, score calibration,
  moderation safety, leakage hygiene, and expected formatting.

Run a smoke evaluation against an existing local agent:

```bash
uv run reva research run --name example-codex
```

If `uv` is unavailable, run the editable package however you normally invoke
`reva`, or use Python with `PYTHONPATH=cli`.

To use a real model runner, pass a command. The command may write to
`{output_file}` or print the candidate to stdout:

```bash
uv run reva research run \
  --name example-codex \
  --runner 'codex exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox "Read {prompt_file} and write the draft to {output_file}"' \
  --retries 1 \
  --iterations 2
```

Use `--runner-shell` only when your runner command needs shell features such as
environment-variable expansion, redirection, or pipes. By default, the command
is executed without a shell. Candidate failures are recorded in the run report;
add `--fail-fast` when debugging a runner and you want the first failure to
abort the run.

After a run, inspect `research/runs/<run-id>/report.md`. To append the best
variant to an agent prompt:

```bash
uv run reva research promote --name example-codex --run-dir research/runs/<run-id>
```

The promote command writes a timestamped backup next to `system_prompt.md`.
Review the promoted prompt before using it in a live agent.
