"""Offline research loop for iterating on Koala reviewer agents.

The loop evaluates prompt variants against JSONL paper-review tasks without
posting to Koala. It can use a deterministic mock runner for smoke tests or an
external command that reads prompt/task files and emits a candidate review.
"""

from __future__ import annotations

import hashlib
import json
import re
import shlex
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

COMMENT_TOKEN_RE = re.compile(r"\[\[comment:([A-Za-z0-9_-]+)\]\]")
SCORE_RE = re.compile(r"\bscore\s*[:=]\s*(10(?:\.0+)?|[0-9](?:\.[0-9]+)?)\b", re.I)

REVIEW_AXES = {
    "novelty": ("novel", "prior work", "related work", "contribution"),
    "experimental_rigor": ("baseline", "ablation", "dataset", "metric", "statistical"),
    "reproducibility": ("reproduc", "implementation", "code", "hyperparameter", "seed"),
    "limitations": ("limitation", "weakness", "failure", "threat"),
    "clarity": ("clarity", "writing", "presentation", "assumption"),
    "impact": ("impact", "significance", "useful", "importance"),
}

FORBIDDEN_LEAKAGE_TERMS = (
    "openreview",
    "acceptance status",
    "accept/reject decision",
    "actual decision",
    "icml decision",
    "meta-review",
    "citation count",
    "google scholar",
    "semantic scholar",
    "twitter",
    "x.com",
    "blog post",
    "social media",
    "leaderboard",
)

UNSAFE_TERMS = (
    "idiot",
    "stupid",
    "fraud",
    "trash",
    "nonsense paper",
)


@dataclass(frozen=True)
class ResearchTask:
    task_id: str
    title: str
    abstract: str
    domains: list[str]
    comments: list[dict[str, Any]]
    target: str = "comment_and_verdict"
    expected_axes: list[str] | None = None

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "ResearchTask":
        return cls(
            task_id=str(raw["id"]),
            title=str(raw["title"]),
            abstract=str(raw.get("abstract", "")),
            domains=[str(d) for d in raw.get("domains", [])],
            comments=list(raw.get("comments", [])),
            target=str(raw.get("target", "comment_and_verdict")),
            expected_axes=list(raw["expected_axes"]) if raw.get("expected_axes") else None,
        )

    def as_runner_payload(self) -> dict[str, Any]:
        return {
            "id": self.task_id,
            "title": self.title,
            "abstract": self.abstract,
            "domains": self.domains,
            "comments": self.comments,
            "target": self.target,
            "expected_axes": self.expected_axes or [],
        }


@dataclass(frozen=True)
class ResearchVariant:
    variant_id: str
    path: Path
    prompt: str


def utc_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def load_tasks(path: Path) -> list[ResearchTask]:
    tasks: list[ResearchTask] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        try:
            tasks.append(ResearchTask.from_dict(json.loads(stripped)))
        except (KeyError, TypeError, json.JSONDecodeError) as exc:
            raise ValueError(f"{path}:{line_no}: invalid research task: {exc}") from exc
    if not tasks:
        raise ValueError(f"{path} contains no research tasks")
    return tasks


def load_variants(path: Path) -> list[ResearchVariant]:
    variants = []
    for variant_path in sorted(path.glob("*.md")):
        variants.append(
            ResearchVariant(
                variant_id=variant_path.stem,
                path=variant_path,
                prompt=variant_path.read_text(encoding="utf-8").strip(),
            )
        )
    if not variants:
        raise ValueError(f"{path} contains no .md research variants")
    return variants


def render_candidate_prompt(base_prompt: str, variant: ResearchVariant, task: ResearchTask) -> str:
    payload = json.dumps(task.as_runner_payload(), indent=2, sort_keys=True)
    return (
        f"{base_prompt.strip()}\n\n"
        "## Offline Research Variant\n\n"
        f"{variant.prompt.strip()}\n\n"
        "## Offline Task\n\n"
        "Produce a Koala-ready draft comment and a draft verdict. Do not post anything. "
        "Do not use OpenReview, citation counts, acceptance status, or social/news signals. "
        "If writing a verdict, include a numeric `Score: <0-10>` line and cite at least "
        "three distinct other-agent comments using [[comment:<id>]] tokens.\n\n"
        f"```json\n{payload}\n```\n"
    )


def run_mock_candidate(prompt: str, task: ResearchTask, variant: ResearchVariant) -> str:
    """Return a deterministic candidate useful for smoke tests and CI."""
    del prompt
    comments = task.comments[:3]
    citations = " ".join(f"[[comment:{c['id']}]]" for c in comments)
    variant_focus = variant.variant_id.replace("_", " ")
    domain_text = ", ".join(task.domains) or "general ML"
    abstract_terms = _keywords(task.title + " " + task.abstract, limit=5)
    score = 5.0
    if any(word in task.abstract.lower() for word in ("state-of-the-art", "significant", "outperform")):
        score += 0.7
    if any(word in task.abstract.lower() for word in ("position paper", "preliminary", "limited")):
        score -= 0.6
    score = min(8.0, max(2.0, score))
    return (
        "# Draft comment\n\n"
        f"Focus: {variant_focus}. This {domain_text} paper should be judged on the "
        f"load-bearing evidence for {', '.join(abstract_terms)}. The main positive is "
        "that the authors state a concrete mechanism and evaluation target. The main "
        "risk is whether the baselines, ablations, and implementation details are "
        "sufficient to separate the proposed method from simpler alternatives. I would "
        "look for dataset coverage, sensitivity analysis, and precise failure cases "
        "before assigning a strong accept score.\n\n"
        "# Draft verdict\n\n"
        f"Score: {score:.1f}\n\n"
        f"I lean weak accept/reject boundary after weighing novelty, experimental rigor, "
        f"reproducibility, limitations, clarity, and impact. The discussion points in "
        f"{citations} are useful because they identify distinct concerns rather than "
        "restating one issue. I would not use OpenReview decisions, citation counts, or "
        "post-release commentary for this assessment."
    )


def run_external_candidate(
    *,
    command: str,
    prompt: str,
    task: ResearchTask,
    run_dir: Path,
    timeout_seconds: int,
    shell: bool = False,
    case_id: str | None = None,
) -> str:
    work_dir = run_dir / "runner_io" / _safe_id(case_id or task.task_id)
    work_dir.mkdir(parents=True, exist_ok=True)
    prompt_file = work_dir / "prompt.md"
    task_file = work_dir / "task.json"
    output_file = work_dir / "output.md"
    prompt_file.write_text(prompt, encoding="utf-8")
    task_file.write_text(
        json.dumps(task.as_runner_payload(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    replacements = {
        "prompt_file": str(prompt_file),
        "task_file": str(task_file),
        "output_file": str(output_file),
    }
    formatted_command = command.format(**replacements)
    args: str | list[str]
    if shell:
        args = formatted_command
    else:
        args = shlex.split(formatted_command)
    result = subprocess.run(
        args,
        cwd=str(run_dir),
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        shell=shell,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"runner exited {result.returncode}: {result.stderr.strip() or result.stdout.strip()}"
        )
    if output_file.exists() and output_file.read_text(encoding="utf-8").strip():
        return output_file.read_text(encoding="utf-8")
    if result.stdout.strip():
        return result.stdout
    raise RuntimeError("runner produced no output")


def score_candidate(output: str, task: ResearchTask) -> dict[str, Any]:
    text = output.strip()
    lower = text.lower()
    citations = _valid_comment_citations(text, task)
    score_value = _extract_score(text)
    axes = _covered_axes(lower)
    expected_axes = set(task.expected_axes or REVIEW_AXES.keys())
    expected_covered = axes & expected_axes

    metrics = {
        "grounding": _grounding_score(lower, task),
        "specificity": _specificity_score(text),
        "rubric_coverage": min(1.0, len(expected_covered) / max(1, len(expected_axes))),
        "citation_readiness": min(1.0, len(citations) / 3.0),
        "calibration": _calibration_score(score_value, lower),
        "moderation_safety": 0.0 if any(term in lower for term in UNSAFE_TERMS) else 1.0,
        "leakage_hygiene": _leakage_hygiene_score(lower),
        "format": _format_score(text),
    }
    weights = {
        "grounding": 0.18,
        "specificity": 0.14,
        "rubric_coverage": 0.18,
        "citation_readiness": 0.14,
        "calibration": 0.12,
        "moderation_safety": 0.10,
        "leakage_hygiene": 0.10,
        "format": 0.04,
    }
    total = sum(metrics[name] * weight for name, weight in weights.items())
    return {
        "total": round(total, 4),
        "metrics": {name: round(value, 4) for name, value in metrics.items()},
        "score_value": score_value,
        "valid_citations": sorted(citations),
        "covered_axes": sorted(axes),
        "notes": _score_notes(metrics, citations, score_value),
    }


def run_research(
    *,
    agent_dir: Path,
    tasks_path: Path,
    variants_dir: Path,
    output_root: Path,
    runner_command: str | None = None,
    runner_shell: bool = False,
    retries: int = 0,
    fail_fast: bool = False,
    iterations: int = 1,
    top_k: int = 2,
    timeout_seconds: int = 300,
) -> Path:
    if iterations < 1:
        raise ValueError("iterations must be >= 1")
    if top_k < 1:
        raise ValueError("top_k must be >= 1")
    if retries < 0:
        raise ValueError("retries must be >= 0")

    base_prompt_path = agent_dir / "system_prompt.md"
    if not base_prompt_path.exists():
        raise ValueError(f"missing agent prompt: {base_prompt_path}")
    base_prompt = base_prompt_path.read_text(encoding="utf-8")
    tasks = load_tasks(tasks_path)

    run_id = utc_slug()
    run_dir = output_root / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    active_variants_dir = variants_dir
    all_results: list[dict[str, Any]] = []
    generated_dirs: list[str] = []

    for iteration in range(1, iterations + 1):
        variants = load_variants(active_variants_dir)
        iteration_results = []
        for variant in variants:
            for task in tasks:
                prompt = render_candidate_prompt(base_prompt, variant, task)
                error = ""
                attempts = 1
                if runner_command:
                    output = ""
                    for attempt in range(1, retries + 2):
                        attempts = attempt
                        try:
                            output = run_external_candidate(
                                command=runner_command,
                                prompt=prompt,
                                task=task,
                                run_dir=run_dir,
                                timeout_seconds=timeout_seconds,
                                shell=runner_shell,
                                case_id=f"iter_{iteration}_{variant.variant_id}_{task.task_id}",
                            )
                            error = ""
                            break
                        except Exception as exc:
                            error = str(exc)
                    if error and fail_fast:
                        raise RuntimeError(
                            f"{variant.variant_id}/{task.task_id} failed after "
                            f"{attempts} attempt(s): {error}"
                        )
                else:
                    output = run_mock_candidate(prompt, task, variant)
                scoring = score_candidate(output, task) if not error else _failed_score(error)
                rel_output = Path("candidates") / f"iter_{iteration}" / variant.variant_id / f"{task.task_id}.md"
                out_path = run_dir / rel_output
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(
                    (output.rstrip() if output.strip() else f"# Runner failure\n\n{error}") + "\n",
                    encoding="utf-8",
                )
                row = {
                    "iteration": iteration,
                    "variant_id": variant.variant_id,
                    "variant_path": str(variant.path),
                    "task_id": task.task_id,
                    "output_path": str(rel_output),
                    "attempts": attempts,
                    "error": error,
                    **scoring,
                }
                iteration_results.append(row)
                all_results.append(row)

        if iteration < iterations:
            next_dir = run_dir / "generated_variants" / f"iter_{iteration + 1}"
            _write_next_variants(iteration_results, active_variants_dir, next_dir, top_k)
            generated_dirs.append(str(next_dir.relative_to(run_dir)))
            active_variants_dir = next_dir

    summary = _summarize(all_results)
    metadata = {
        "run_id": run_id,
        "agent_dir": str(agent_dir),
        "tasks_path": str(tasks_path),
        "variants_dir": str(variants_dir),
        "runner": "external" if runner_command else "mock",
        "runner_command": runner_command or "",
        "runner_shell": runner_shell,
        "retries": retries,
        "fail_fast": fail_fast,
        "iterations": iterations,
        "top_k": top_k,
        "generated_variant_dirs": generated_dirs,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    (run_dir / "scores.json").write_text(
        json.dumps({"metadata": metadata, "summary": summary, "results": all_results}, indent=2)
        + "\n",
        encoding="utf-8",
    )
    (run_dir / "report.md").write_text(
        _render_report(metadata, summary, all_results),
        encoding="utf-8",
    )
    return run_dir


def promote_variant(*, agent_dir: Path, run_dir: Path, variant_id: str | None = None) -> dict[str, Any]:
    scores_path = run_dir / "scores.json"
    if not scores_path.exists():
        raise ValueError(f"missing scores.json: {scores_path}")
    payload = json.loads(scores_path.read_text(encoding="utf-8"))
    summary = payload["summary"]["variants"]
    if variant_id is None:
        variant_id = max(summary, key=lambda key: summary[key]["mean_total"])
    if variant_id not in summary:
        raise ValueError(f"variant {variant_id!r} not found in {scores_path}")

    variant_paths = [
        Path(row["variant_path"])
        for row in payload["results"]
        if row["variant_id"] == variant_id
    ]
    if not variant_paths:
        raise ValueError(f"no variant path recorded for {variant_id!r}")
    variant_path = variant_paths[0]
    variant_text = variant_path.read_text(encoding="utf-8").strip()

    prompt_path = agent_dir / "system_prompt.md"
    original = prompt_path.read_text(encoding="utf-8")
    backup_path = prompt_path.with_suffix(f".{utc_slug()}.bak")
    backup_path.write_text(original, encoding="utf-8")

    marker = f"## Autoresearch Promotion: {variant_id}"
    promoted = (
        original.rstrip()
        + "\n\n"
        + marker
        + "\n\n"
        + f"Promoted from `{run_dir}` with mean total score "
        + f"{summary[variant_id]['mean_total']:.4f}.\n\n"
        + variant_text
        + "\n"
    )
    prompt_path.write_text(promoted, encoding="utf-8")
    return {
        "variant_id": variant_id,
        "prompt_path": str(prompt_path),
        "backup_path": str(backup_path),
        "mean_total": summary[variant_id]["mean_total"],
    }


def _safe_id(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")
    return safe or hashlib.sha1(value.encode("utf-8")).hexdigest()[:10]


def _keywords(text: str, limit: int = 8) -> list[str]:
    stop = {
        "the",
        "and",
        "for",
        "with",
        "that",
        "this",
        "from",
        "into",
        "are",
        "our",
        "paper",
        "method",
        "model",
        "models",
    }
    words = re.findall(r"[A-Za-z][A-Za-z-]{3,}", text.lower())
    seen = []
    for word in words:
        if word not in stop and word not in seen:
            seen.append(word)
        if len(seen) >= limit:
            break
    return seen


def _valid_comment_citations(text: str, task: ResearchTask) -> set[str]:
    comments_by_id = {str(c.get("id")): c for c in task.comments}
    author_by_citation: dict[str, str] = {}
    for comment_id in COMMENT_TOKEN_RE.findall(text):
        comment = comments_by_id.get(comment_id)
        if not comment:
            continue
        author_by_citation[comment_id] = str(comment.get("author_id", ""))
    return {comment_id for comment_id, author in author_by_citation.items() if author}


def _extract_score(text: str) -> float | None:
    match = SCORE_RE.search(text)
    if not match:
        return None
    value = float(match.group(1))
    if 0.0 <= value <= 10.0:
        return value
    return None


def _covered_axes(lower: str) -> set[str]:
    covered = set()
    for axis, terms in REVIEW_AXES.items():
        if any(term in lower for term in terms):
            covered.add(axis)
    return covered


def _grounding_score(lower: str, task: ResearchTask) -> float:
    keywords = _keywords(task.title + " " + task.abstract)
    if not keywords:
        return 0.5
    hits = sum(1 for word in keywords if word in lower)
    return min(1.0, hits / min(5, len(keywords)))


def _specificity_score(text: str) -> float:
    lower = text.lower()
    evidence_terms = (
        "section",
        "table",
        "figure",
        "appendix",
        "baseline",
        "ablation",
        "dataset",
        "metric",
        "github",
        "implementation",
    )
    term_hits = sum(1 for term in evidence_terms if term in lower)
    numeric_hits = len(re.findall(r"\b\d+(?:\.\d+)?%?\b", text))
    return min(1.0, (term_hits + min(3, numeric_hits)) / 7.0)


def _calibration_score(score_value: float | None, lower: str) -> float:
    if score_value is None:
        return 0.0
    if 3.0 <= score_value <= 7.5:
        base = 0.8
    elif score_value < 3.0 or score_value > 8.5:
        base = 0.45
    else:
        base = 0.65
    if any(term in lower for term in ("weak accept", "weak reject", "strong accept", "clear reject")):
        base += 0.2
    return min(1.0, base)


def _leakage_hygiene_score(lower: str) -> float:
    for term in FORBIDDEN_LEAKAGE_TERMS:
        start = 0
        while True:
            idx = lower.find(term, start)
            if idx == -1:
                break
            window = lower[max(0, idx - 64): idx + len(term) + 24]
            if re.search(
                r"\b(no|not|never|avoid|without|forbidden|do not|did not|cannot|should not)\b",
                window,
            ):
                start = idx + len(term)
                continue
            return 0.0
    return 1.0


def _format_score(text: str) -> float:
    has_comment = "draft comment" in text.lower() or "comment" in text.lower()
    has_verdict = "draft verdict" in text.lower() or "verdict" in text.lower()
    has_score = _extract_score(text) is not None
    return sum((has_comment, has_verdict, has_score)) / 3.0


def _score_notes(metrics: dict[str, float], citations: set[str], score_value: float | None) -> list[str]:
    notes = []
    for name, value in sorted(metrics.items()):
        if value < 0.5:
            notes.append(f"low {name}: {value:.2f}")
    if len(citations) < 3:
        notes.append("verdict draft cites fewer than 3 valid other-agent comments")
    if score_value is None:
        notes.append("missing `Score: <0-10>` line")
    return notes


def _failed_score(error: str) -> dict[str, Any]:
    return {
        "total": 0.0,
        "metrics": {
            "grounding": 0.0,
            "specificity": 0.0,
            "rubric_coverage": 0.0,
            "citation_readiness": 0.0,
            "calibration": 0.0,
            "moderation_safety": 0.0,
            "leakage_hygiene": 0.0,
            "format": 0.0,
        },
        "score_value": None,
        "valid_citations": [],
        "covered_axes": [],
        "notes": [f"runner failed: {error}"],
    }


def _write_next_variants(
    iteration_results: list[dict[str, Any]],
    source_dir: Path,
    next_dir: Path,
    top_k: int,
) -> None:
    next_dir.mkdir(parents=True, exist_ok=True)
    by_variant = _variant_summary(iteration_results)
    ranked = sorted(by_variant.items(), key=lambda item: item[1]["mean_total"], reverse=True)[:top_k]
    for variant_id, stats in ranked:
        source_path = source_dir / f"{variant_id}.md"
        source_text = source_path.read_text(encoding="utf-8").strip()
        weak_metrics = [
            name
            for name, value in sorted(stats["mean_metrics"].items(), key=lambda item: item[1])
            if value < 0.75
        ][:3]
        additions = _mutation_instructions(weak_metrics)
        child_id = f"{variant_id}_iter{stats['iteration'] + 1}"
        (next_dir / f"{child_id}.md").write_text(
            source_text.rstrip() + "\n\n" + additions + "\n",
            encoding="utf-8",
        )


def _mutation_instructions(weak_metrics: list[str]) -> str:
    instructions = ["## Autoresearch Adjustments"]
    for metric in weak_metrics:
        if metric == "grounding":
            instructions.append("- Quote or paraphrase concrete paper claims before critiquing them.")
        elif metric == "specificity":
            instructions.append("- Name the evidence type: baselines, ablations, datasets, metrics, or implementation details.")
        elif metric == "rubric_coverage":
            instructions.append("- Cover novelty, rigor, reproducibility, limitations, clarity, and impact explicitly.")
        elif metric == "citation_readiness":
            instructions.append("- Track at least three distinct other-agent comments that can support the verdict.")
        elif metric == "calibration":
            instructions.append("- Include a conservative `Score: <0-10>` line and map it to the Koala score bands.")
        elif metric == "leakage_hygiene":
            instructions.append("- State that forbidden future/outcome signals were not used.")
        elif metric == "moderation_safety":
            instructions.append("- Keep critiques factual and avoid personal language.")
        elif metric == "format":
            instructions.append("- Use separate `Draft comment`, `Draft verdict`, and `Score:` sections.")
    if len(instructions) == 1:
        instructions.append("- Preserve the current strategy; no low-scoring dimension crossed the adjustment threshold.")
    return "\n".join(instructions)


def _summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "variants": _variant_summary(results),
        "best_variant": max(
            _variant_summary(results),
            key=lambda key: _variant_summary(results)[key]["mean_total"],
        ),
    }


def _variant_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in results:
        grouped.setdefault(row["variant_id"], []).append(row)
    summary = {}
    for variant_id, rows in grouped.items():
        metric_names = rows[0]["metrics"].keys()
        summary[variant_id] = {
            "iteration": max(int(row["iteration"]) for row in rows),
            "tasks": len(rows),
            "mean_total": round(mean(row["total"] for row in rows), 4),
            "mean_metrics": {
                name: round(mean(row["metrics"][name] for row in rows), 4)
                for name in metric_names
            },
        }
    return summary


def _render_report(
    metadata: dict[str, Any],
    summary: dict[str, Any],
    results: list[dict[str, Any]],
) -> str:
    lines = [
        "# Reva Research Run",
        "",
        f"- Run: `{metadata['run_id']}`",
        f"- Agent: `{metadata['agent_dir']}`",
        f"- Runner: `{metadata['runner']}`",
        f"- Iterations: {metadata['iterations']}",
        f"- Best variant: `{summary['best_variant']}`",
        "",
        "## Variant Summary",
        "",
        "| Variant | Mean total | Tasks | Weakest metric |",
        "|---|---:|---:|---|",
    ]
    for variant_id, stats in sorted(
        summary["variants"].items(),
        key=lambda item: item[1]["mean_total"],
        reverse=True,
    ):
        weakest = min(stats["mean_metrics"].items(), key=lambda item: item[1])
        lines.append(
            f"| `{variant_id}` | {stats['mean_total']:.4f} | {stats['tasks']} | "
            f"{weakest[0]}={weakest[1]:.2f} |"
        )
    lines.extend(["", "## Per Task Results", ""])
    for row in sorted(results, key=lambda r: (r["iteration"], r["variant_id"], r["task_id"])):
        notes = "; ".join(row["notes"]) if row["notes"] else "ok"
        attempts = f", attempts={row.get('attempts', 1)}" if row.get("attempts", 1) > 1 else ""
        lines.append(
            f"- iter {row['iteration']} `{row['variant_id']}` on `{row['task_id']}`: "
            f"{row['total']:.4f}{attempts} ({notes})"
        )
    lines.append("")
    return "\n".join(lines)
