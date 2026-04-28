import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from reva.cli import main
from reva.research import promote_variant, run_research, score_candidate


def _write_agent(tmp_path: Path) -> Path:
    agent_dir = tmp_path / "agents" / "alpha"
    agent_dir.mkdir(parents=True)
    (agent_dir / "system_prompt.md").write_text("# Agent alpha\n\nReview carefully.\n", encoding="utf-8")
    (agent_dir / "config.json").write_text(
        json.dumps({"name": "alpha", "backend": "codex"}),
        encoding="utf-8",
    )
    return agent_dir


def _write_tasks(tmp_path: Path) -> Path:
    tasks = tmp_path / "tasks.jsonl"
    tasks.write_text(
        json.dumps(
            {
                "id": "task1",
                "title": "Ablation-Rich Learning System",
                "abstract": "The paper reports baselines, ablations, datasets, and implementation details.",
                "domains": ["d/NLP"],
                "expected_axes": ["novelty", "experimental_rigor", "reproducibility"],
                "comments": [
                    {"id": "c1", "author_id": "a1", "content_markdown": "baseline concern"},
                    {"id": "c2", "author_id": "a2", "content_markdown": "ablation concern"},
                    {"id": "c3", "author_id": "a3", "content_markdown": "repro concern"},
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return tasks


def _write_variants(tmp_path: Path) -> Path:
    variants = tmp_path / "variants"
    variants.mkdir()
    (variants / "baseline.md").write_text(
        "Cover novelty, experimental rigor, reproducibility, limitations, clarity, and impact.\n",
        encoding="utf-8",
    )
    return variants


def _write_two_variants(tmp_path: Path) -> Path:
    variants = _write_variants(tmp_path)
    (variants / "second.md").write_text("Cover implementation details and calibration.\n", encoding="utf-8")
    return variants


def test_score_candidate_rewards_valid_citations_and_format():
    from reva.research import ResearchTask

    parsed = ResearchTask.from_dict(
        {
            "id": "task1",
            "title": "Ablation-Rich Learning System",
            "abstract": "The paper reports baselines, ablations, datasets, and implementation details.",
            "domains": ["d/NLP"],
            "expected_axes": ["novelty", "experimental_rigor", "reproducibility"],
            "comments": [
                {"id": "c1", "author_id": "a1", "content_markdown": "baseline concern"},
                {"id": "c2", "author_id": "a2", "content_markdown": "ablation concern"},
                {"id": "c3", "author_id": "a3", "content_markdown": "repro concern"},
            ],
        }
    )
    output = (
        "Draft comment: The paper has baselines, ablations, datasets, and code details.\n\n"
        "Draft verdict\n\n"
        "Score: 5.5\n\n"
        "Novelty, experimental rigor, reproducibility, limitations, clarity, and impact "
        "are considered. [[comment:c1]] [[comment:c2]] [[comment:c3]]"
    )
    scored = score_candidate(output, parsed)
    assert scored["total"] > 0.7
    assert scored["score_value"] == 5.5
    assert scored["valid_citations"] == ["c1", "c2", "c3"]


def test_run_research_mock_writes_report_and_scores(tmp_path):
    agent_dir = _write_agent(tmp_path)
    run_dir = run_research(
        agent_dir=agent_dir,
        tasks_path=_write_tasks(tmp_path),
        variants_dir=_write_variants(tmp_path),
        output_root=tmp_path / "runs",
    )
    assert (run_dir / "report.md").exists()
    scores = json.loads((run_dir / "scores.json").read_text(encoding="utf-8"))
    assert scores["metadata"]["runner"] == "mock"
    assert scores["summary"]["best_variant"] == "baseline"
    assert len(scores["results"]) == 1


def test_run_research_records_runner_failure_without_fail_fast(tmp_path):
    agent_dir = _write_agent(tmp_path)
    run_dir = run_research(
        agent_dir=agent_dir,
        tasks_path=_write_tasks(tmp_path),
        variants_dir=_write_variants(tmp_path),
        output_root=tmp_path / "runs",
        runner_command='python3 -c "import sys; sys.exit(3)"',
        retries=1,
    )
    scores = json.loads((run_dir / "scores.json").read_text(encoding="utf-8"))
    row = scores["results"][0]
    assert row["total"] == 0.0
    assert row["attempts"] == 2
    assert "runner failed" in row["notes"][0]


def test_run_research_fail_fast_raises_on_runner_failure(tmp_path):
    agent_dir = _write_agent(tmp_path)
    with pytest.raises(RuntimeError):
        run_research(
            agent_dir=agent_dir,
            tasks_path=_write_tasks(tmp_path),
            variants_dir=_write_variants(tmp_path),
            output_root=tmp_path / "runs",
            runner_command='python3 -c "import sys; sys.exit(3)"',
            fail_fast=True,
        )


def test_run_research_shell_runner_can_write_output_file(tmp_path):
    agent_dir = _write_agent(tmp_path)
    run_dir = run_research(
        agent_dir=agent_dir,
        tasks_path=_write_tasks(tmp_path),
        variants_dir=_write_variants(tmp_path),
        output_root=tmp_path / "runs",
        runner_command="printf 'Draft comment\\n\\nDraft verdict\\n\\nScore: 5.0 [[comment:c1]] [[comment:c2]] [[comment:c3]]' > {output_file}",
        runner_shell=True,
    )
    scores = json.loads((run_dir / "scores.json").read_text(encoding="utf-8"))
    assert scores["results"][0]["error"] == ""
    assert scores["results"][0]["valid_citations"] == ["c1", "c2", "c3"]


def test_run_research_preserves_runner_io_per_variant(tmp_path):
    agent_dir = _write_agent(tmp_path)
    run_dir = run_research(
        agent_dir=agent_dir,
        tasks_path=_write_tasks(tmp_path),
        variants_dir=_write_two_variants(tmp_path),
        output_root=tmp_path / "runs",
        runner_command="printf 'Draft comment\\n\\nDraft verdict\\n\\nScore: 5.0 [[comment:c1]] [[comment:c2]] [[comment:c3]]' > {output_file}",
        runner_shell=True,
    )
    runner_dirs = sorted((run_dir / "runner_io").iterdir())
    assert len(runner_dirs) == 2
    assert all((path / "prompt.md").exists() for path in runner_dirs)


def test_promote_variant_appends_to_agent_prompt_and_backs_up(tmp_path):
    agent_dir = _write_agent(tmp_path)
    run_dir = run_research(
        agent_dir=agent_dir,
        tasks_path=_write_tasks(tmp_path),
        variants_dir=_write_variants(tmp_path),
        output_root=tmp_path / "runs",
    )
    result = promote_variant(agent_dir=agent_dir, run_dir=run_dir)
    prompt = (agent_dir / "system_prompt.md").read_text(encoding="utf-8")
    assert result["variant_id"] == "baseline"
    assert "Autoresearch Promotion: baseline" in prompt
    assert Path(result["backup_path"]).exists()


def test_research_cli_run_uses_project_defaults(tmp_path):
    agent_dir = _write_agent(tmp_path)
    research_dir = tmp_path / "research"
    (research_dir / "tasks").mkdir(parents=True)
    (research_dir / "variants").mkdir(parents=True)
    (research_dir / "tasks" / "smoke.jsonl").write_text(
        _write_tasks(tmp_path).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (research_dir / "variants" / "baseline.md").write_text(
        "Cover novelty and rigor.\n",
        encoding="utf-8",
    )

    cfg = MagicMock()
    cfg.project_root = tmp_path
    cfg.agents_dir = agent_dir.parent

    runner = CliRunner()
    with patch("reva.cli._get_config", return_value=cfg):
        result = runner.invoke(
            main,
            ["research", "run", "--name", "alpha"],
            catch_exceptions=False,
        )

    assert result.exit_code == 0, result.output
    assert "Research run written to:" in result.output
    assert any((research_dir / "runs").iterdir())


def test_reva_cli_module_is_directly_invokable():
    import os
    import subprocess
    import sys

    env = os.environ.copy()
    env["PYTHONPATH"] = "cli"
    result = subprocess.run(
        [sys.executable, "-m", "reva.cli", "--help"],
        cwd=Path(__file__).resolve().parents[1],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "reva — reviewer agent CLI" in result.stdout
