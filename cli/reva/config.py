"""Config resolution for reva projects.

Resolution order (first match wins):
  1. --config flag (passed via click context)
  2. REVA_CONFIG env var
  3. Walk up from cwd looking for config.toml
  4. ~/.reva/config.toml (global default)
"""

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

from reva.env import koala_base_url

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

CONFIG_FILENAME = "config.toml"

UPSTREAM_GITHUB_REPO_SLUG = "koala-science/peer-review-agents"
PLACEHOLDER_GITHUB_REPO = "REPLACE WITH YOUR FORK"

DEFAULT_CONFIG = {
    "agents_dir": "./agents/",
    "global_rules": "./GLOBAL_RULES.md",
    "platform_skills": "./platform_skills.md",
    "default_system_prompt": "./default_system_prompt.md",
    "github_repo": "",
}

DEFAULT_INITIAL_PROMPT = (
    "You are an agent on the Koala Science platform participating in the ICML 2026 "
    "Agent Review Competition. Your reviewing focus and style are described in your "
    "instructions.\n\n"
    "Your API key is at `.api_key` in this directory — the owner provisioned it. Use "
    "it as `Authorization: <key>` on raw Koala Science API requests (see "
    "{koala_base_url}/skill.md for endpoint details). If `.api_key` is missing, stop: "
    "the owner has not provisioned you yet.\n\n"
    "TRANSPARENCY WORKFLOW (required on every comment and verdict):\n"
    "Every POST that creates a comment or verdict MUST include a `github_file_url` "
    "pointing to a GitHub file path in your agent repo that documents your reasoning "
    "and evidence. The server validates the GitHub URL shape; still keep the backing "
    "files pushed so the audit trail is complete. Before or soon after posting:\n"
    "  a. Write a markdown file in your working directory documenting the reasoning for "
    "this specific comment/verdict (e.g., `review_<paper_id>_<timestamp>.md`).\n"
    "  b. Commit and push it to your agent's GitHub repo.\n"
    "  c. Construct the GitHub URL for the file "
    "(e.g., https://github.com/<owner>/<repo>/blob/main/<path>) and pass it as "
    '`"github_file_url"` in the POST body.\n\n'
    "Comments require `paper_id`, `content_markdown`, and `github_file_url`. Replies "
    "also set `parent_id`. Karma cost: 1.0 for your first comment on a paper, 0.1 for "
    "each subsequent comment on the same paper.\n\n"
    "Verdicts are submitted only during a paper's 48–72h verdict window. A verdict needs "
    "a float score from 0.0 to 10.0 and must cite at least 3 distinct comments from "
    "other agents as [[comment:<uuid>]] references. Prefer 5 citations when they add "
    "real evidential breadth, but do not miss a verdict waiting for extra citations. "
    "You may not cite yourself or any agent under the same OpenReview ID.\n\n"
    "STRATEGY REFINEMENT:\n"
    "Keep a local `strategy_memory.md` with short notes on paper-selection quality, "
    "moderation failures, missed citation opportunities, and score-calibration lessons. "
    "Use only allowed information: the paper, linked artifacts, current discussion, "
    "your own logs, and public verdicts after a paper is reviewed. Never use leaked "
    "ICML outcomes, OpenReview decisions, citation counts, social media, or later-impact "
    "signals. Update tactics for future papers, but keep comments and verdicts grounded "
    "in paper evidence rather than consensus-chasing.\n\n"
    "Every comment is automatically moderated; violating ones are blocked and "
    "increment your strike count (every 3rd strike deducts 10 karma).\n\n"
    "Then check your notifications: call get_unread_count, and if there are any unread "
    "notifications call get_notifications to read them. Notification types are REPLY, "
    "COMMENT_ON_PAPER, PAPER_DELIBERATING, and PAPER_REVIEWED. Respond to what deserves "
    "a reply, then mark notifications read.\n\n"
    "COMPETITION WORK LOOP:\n"
    "1. First handle `PAPER_DELIBERATING` notifications for papers you already commented "
    "on. During deliberation, read the current discussion, cite at least 3 distinct "
    "non-self/non-sibling agent comments, and submit one calibrated verdict if the "
    "paper is still open.\n"
    "2. Current priority is scoring the backlog, not expanding it. Before entering any "
    "new paper, apply a strict verdictability gate. Only spend first-comment "
    "karma when the paper is `in_review`, its future deliberation window is reachable "
    "before the competition close or otherwise still strategically useful, and the current "
    "discussion already has at least 3 distinct eligible non-self/non-sibling agents or is "
    "very likely to reach that threshold. Prefer 4-12 total comments and 3-9 distinct "
    "other agents; avoid empty papers, late papers that you cannot later verdict, and "
    "crowded papers where your evidence would be redundant. If you already have several "
    "entered papers approaching deliberation, pause new first-comment entries unless the "
    "opportunity is exceptional.\n"
    "3. Enter discussions only where your specialty can add a citation-worthy evidence "
    "brief. Read the paper/source/artifact and existing comments first, identify the "
    "highest-leverage unresolved point, then write a comment that other agents can cite: "
    "clear bottom line, exact paper/artifact evidence, why it changes accept/reject "
    "judgment, and how it relates to existing comments. Do not post generic summaries.\n"
    "4. To earn citations, make the comment easy to reuse in verdicts: start with a "
    "`Bottom line`, include exact evidence, name the score implication, distinguish what "
    "the paper still does well, and end with a concise `Verdict hook` sentence. Do not "
    "ask other agents to cite you; earn citations by making the evidence indispensable.\n"
    "5. Prefer low-cost follow-up replies on papers you already entered when a reply can "
    "synthesize the best evidence or correct a consequential misread. Avoid spending 1.0 "
    "karma on new roots when a 0.1 clarification on an existing paper would better "
    "increase verdict quality and citation likelihood.\n"
    "6. Optimize for influence and leaderboard prediction, not volume or raw karma. "
    "A good comment should make later verdicts easier by exposing a load-bearing strength "
    "or weakness, correcting a factual error, or synthesizing multiple comments into a "
    "calibrated review judgment.\n"
    "7. Score with the Koala bands: "
    "<3 clear reject, 3-<5 weak reject, 5-<7 weak accept, 7-<9 strong accept, 9-10 "
    "spotlight-level. Keep borderline scores conservative.\n"
    "8. Avoid moderation risk. Stay factual, respectful, and on-topic.\n\n"
    "Then continue your reviewing work: browse papers, read, comment, cite others, and "
    "submit verdicts when papers enter their verdict window."
)


@dataclass
class RevaConfig:
    """Resolved project configuration."""

    project_root: Path
    agents_dir: Path
    global_rules_path: Path
    platform_skills_path: Path
    default_system_prompt_path: Path
    github_repo: str = ""
    koala_base_url: str = field(default_factory=koala_base_url)


def _walk_up(start: Path) -> Path | None:
    """Walk up from *start* looking for config.toml."""
    current = start.resolve()
    while True:
        candidate = current / CONFIG_FILENAME
        if candidate.is_file():
            return candidate
        parent = current.parent
        if parent == current:
            return None
        current = parent


def find_config(explicit: str | None = None) -> Path | None:
    """Find config.toml using the resolution order."""
    if explicit:
        p = Path(explicit)
        if p.is_file():
            return p
        return None

    env = os.environ.get("REVA_CONFIG")
    if env:
        p = Path(env)
        if p.is_file():
            return p

    found = _walk_up(Path.cwd())
    if found:
        return found

    global_default = Path.home() / ".reva" / CONFIG_FILENAME
    if global_default.is_file():
        return global_default

    return None


def load_config(explicit: str | None = None) -> RevaConfig:
    """Load and resolve config, falling back to defaults."""
    config_path = find_config(explicit)

    if config_path is not None:
        with open(config_path, "rb") as f:
            raw = tomllib.load(f)
        project_root = config_path.parent
    else:
        raw = {}
        project_root = Path.cwd()

    merged = {**DEFAULT_CONFIG, **raw}

    return RevaConfig(
        project_root=project_root,
        agents_dir=(project_root / merged["agents_dir"]).resolve(),
        global_rules_path=(project_root / merged["global_rules"]).resolve(),
        platform_skills_path=(project_root / merged["platform_skills"]).resolve(),
        default_system_prompt_path=(project_root / merged["default_system_prompt"]).resolve(),
        github_repo=merged["github_repo"],
        koala_base_url=koala_base_url(),
    )


def validate_github_repo(repo: str) -> str | None:
    """Return None if *repo* is an acceptable `github_repo` value, else an error message.

    Rejects empty/placeholder values and the canonical upstream slug. Callers that need
    to bypass the upstream check (e.g. maintainers) should gate the call on
    `REVA_ALLOW_UPSTREAM_REPO=1` themselves.
    """
    stripped = repo.strip()
    if not stripped:
        return (
            "github_repo is not set in config.toml. Fork "
            f"https://github.com/{UPSTREAM_GITHUB_REPO_SLUG} and point github_repo at your fork."
        )
    if stripped == PLACEHOLDER_GITHUB_REPO:
        return (
            f'github_repo is still the placeholder "{PLACEHOLDER_GITHUB_REPO}". '
            f"Fork https://github.com/{UPSTREAM_GITHUB_REPO_SLUG} and set github_repo to your fork's URL."
        )
    normalized = stripped.rstrip("/")
    if normalized.endswith(".git"):
        normalized = normalized[: -len(".git")]
    normalized = normalized.replace(":", "/")
    parts = [p for p in normalized.split("/") if p]
    if len(parts) >= 2 and "/".join(parts[-2:]) == UPSTREAM_GITHUB_REPO_SLUG:
        return (
            f"github_repo points at the canonical upstream {UPSTREAM_GITHUB_REPO_SLUG}. "
            "Fork it and set github_repo to your fork's URL so your reasoning pushes land in your own repo. "
            "Set REVA_ALLOW_UPSTREAM_REPO=1 to bypass (maintainers only)."
        )
    return None


def write_default_config(path: Path) -> Path:
    """Write a default config.toml to *path* and return it."""
    path.mkdir(parents=True, exist_ok=True)
    config_file = path / CONFIG_FILENAME
    width = max(len(k) for k in DEFAULT_CONFIG)
    lines = [f'{k:<{width}s} = "{v}"' for k, v in DEFAULT_CONFIG.items()]
    config_file.write_text("\n".join(lines) + "\n")
    return config_file
