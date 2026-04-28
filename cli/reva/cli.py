"""reva CLI — reviewer agent command-line tool."""

import json
import os
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path

import click
from dotenv import load_dotenv

from reva.backends import BACKEND_CHOICES, get_backend
from reva.cluster import cancel_chain, list_cluster_jobs, submit_agent
from reva.config import (
    DEFAULT_INITIAL_PROMPT,
    find_config,
    load_config,
    validate_github_repo,
    write_default_config,
)
from reva.launch_script import write_launch_files
from reva.prompt import assemble_prompt
from reva.registration import (
    OWNER_TOKEN_FILENAME,
    KoalaApiError,
    create_agent as register_koala_agent,
    list_agents as list_registered_agents,
    login_owner,
    read_owner_token,
    save_agent_credentials,
    save_owner_token,
    signup_owner,
    split_openreview_ids,
)
from reva.tmux import (
    build_launch_script,
    create_session,
    has_session,
    kill_all_sessions,
    kill_session,
    list_sessions,
)

def _load_project_env(config_path: str | None) -> None:
    """Load the project's `.env` so env-driven settings reach every subcommand."""
    found = find_config(config_path)
    project_root = found.parent if found is not None else Path.cwd()
    load_dotenv(project_root / ".env", override=False)


@click.group()
@click.option("--config", "config_path", default=None, help="Path to config.toml.")
@click.pass_context
def main(ctx, config_path):
    """reva — reviewer agent CLI."""
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config_path
    _load_project_env(config_path)


def _get_config(ctx):
    return load_config(ctx.obj.get("config_path"))


def _token_file_path(cfg, token_file: str) -> Path:
    path = Path(token_file)
    return path if path.is_absolute() else cfg.project_root / path


def _create_agent_files(cfg, *, name: str, backend: str) -> Path:
    agent_dir = cfg.agents_dir / name
    if agent_dir.exists():
        raise click.ClickException(f"Agent directory already exists: {agent_dir}")
    agent_dir.mkdir(parents=True)

    starter_template = cfg.default_system_prompt_path.read_text(encoding="utf-8")
    (agent_dir / "system_prompt.md").write_text(
        starter_template.replace("{name}", name), encoding="utf-8"
    )

    config_data = {
        "name": name,
        "backend": backend,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    (agent_dir / "config.json").write_text(
        json.dumps(config_data, indent=2), encoding="utf-8"
    )
    (agent_dir / ".agent_name").write_text(name, encoding="utf-8")
    return agent_dir


def _resolve_owner_token(
    cfg,
    *,
    owner_token: str | None,
    token_file: str,
    email: str | None = None,
    password: str | None = None,
) -> str:
    if owner_token:
        return owner_token.strip()

    env_token = os.environ.get("KOALA_OWNER_TOKEN", "").strip()
    if env_token:
        return env_token

    path = _token_file_path(cfg, token_file)
    saved = read_owner_token(path)
    if saved:
        return saved

    if email:
        if password is None:
            password = click.prompt("Koala password", hide_input=True)
        try:
            result = login_owner(
                email=email,
                password=password,
                base_url=cfg.koala_base_url,
            )
        except KoalaApiError as exc:
            raise click.ClickException(str(exc))
        token = result["access_token"]
        save_owner_token(path, token)
        return token

    raise click.ClickException(
        f"Owner token missing. Run `reva login --email <email>` first, "
        f"or pass --owner-token, or set KOALA_OWNER_TOKEN."
    )


def _default_agent_description(agent_dir: Path, name: str) -> str:
    prompt_path = agent_dir / "system_prompt.md"
    if prompt_path.exists():
        for line in prompt_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip(" #")
            if stripped and "TODO" not in stripped and stripped.lower() != f"agent: {name}".lower():
                return stripped[:240]
    return f"Koala peer-review agent: {name}"


# --------------------------------------------------------------------------- #
# reva init
# --------------------------------------------------------------------------- #


@main.command()
@click.argument("path", default=".", type=click.Path())
@click.pass_context
def init(ctx, path):
    """Initialize a reva project (creates config.toml)."""
    target = Path(path).resolve()
    config_file = write_default_config(target)
    cfg = load_config(str(config_file))
    cfg.agents_dir.mkdir(parents=True, exist_ok=True)
    click.echo(f"Initialized reva project at {target}")
    click.echo(f"  config: {config_file}")


# --------------------------------------------------------------------------- #
# reva create
# --------------------------------------------------------------------------- #


@main.command()
@click.option("--name", required=True, help="Agent name (slug).")
@click.option(
    "--backend",
    type=click.Choice(BACKEND_CHOICES),
    default="claude-code",
    show_default=True,
    help="Agent backend.",
)
@click.pass_context
def create(ctx, name, backend):
    """Create a new agent directory with a starter system prompt."""
    cfg = _get_config(ctx)
    agent_dir = _create_agent_files(cfg, name=name, backend=backend)

    click.echo(f"Created agent: {name}")
    click.echo(f"  directory: {agent_dir}")
    click.echo(f"  backend:   {backend}")
    click.echo(
        f"  next steps: edit {agent_dir / 'system_prompt.md'}, drop a key at "
        f"{agent_dir / '.api_key'}, then `reva launch --name {name}`"
    )


# --------------------------------------------------------------------------- #
# reva signup / login / register
# --------------------------------------------------------------------------- #


@main.command()
@click.option("--email", required=True, help="Koala owner email.")
@click.option("--password", prompt=True, hide_input=True, help="Koala owner password.")
@click.option("--owner-name", required=True, help="Human owner display name.")
@click.option(
    "--openreview-id",
    "openreview_ids",
    multiple=True,
    required=True,
    help="OpenReview profile id. Repeat or comma-separate for a team, max 3.",
)
@click.option(
    "--token-file",
    default=OWNER_TOKEN_FILENAME,
    show_default=True,
    help="Where to store the owner access token, relative to the project root.",
)
@click.pass_context
def signup(ctx, email, password, owner_name, openreview_ids, token_file):
    """Create a Koala human owner account and save its access token."""
    cfg = _get_config(ctx)
    ids = split_openreview_ids(openreview_ids)
    if not ids:
        raise click.ClickException("Provide at least one --openreview-id.")
    if len(ids) > 3:
        raise click.ClickException("Koala accepts at most 3 OpenReview IDs per team.")
    try:
        result = signup_owner(
            email=email,
            password=password,
            name=owner_name,
            openreview_ids=ids,
            base_url=cfg.koala_base_url,
        )
    except KoalaApiError as exc:
        raise click.ClickException(str(exc))
    path = _token_file_path(cfg, token_file)
    save_owner_token(path, result["access_token"])
    click.echo(f"Signed up owner: {result['name']} ({result['actor_id']})")
    click.echo(f"  token: {path}")


@main.command()
@click.option("--email", required=True, help="Koala owner email.")
@click.option("--password", prompt=True, hide_input=True, help="Koala owner password.")
@click.option(
    "--token-file",
    default=OWNER_TOKEN_FILENAME,
    show_default=True,
    help="Where to store the owner access token, relative to the project root.",
)
@click.pass_context
def login(ctx, email, password, token_file):
    """Log in as a Koala human owner and save its access token."""
    cfg = _get_config(ctx)
    try:
        result = login_owner(
            email=email,
            password=password,
            base_url=cfg.koala_base_url,
        )
    except KoalaApiError as exc:
        raise click.ClickException(str(exc))
    path = _token_file_path(cfg, token_file)
    save_owner_token(path, result["access_token"])
    click.echo(f"Logged in owner: {result['name']} ({result['actor_id']})")
    click.echo(f"  token: {path}")


@main.command(name="register")
@click.option("--name", required=True, help="Local agent name to register on Koala.")
@click.option(
    "--backend",
    type=click.Choice(BACKEND_CHOICES),
    default="claude-code",
    show_default=True,
    help="Backend to use if the local agent directory does not exist.",
)
@click.option("--description", default=None, help="Public Koala profile description.")
@click.option("--github-repo", default=None, help="Override config.toml github_repo.")
@click.option("--owner-token", default=None, help="Koala human owner access token.")
@click.option("--email", default=None, help="Log in with this owner email if no token is saved.")
@click.option("--password", default=None, hide_input=True, help="Owner password for --email login.")
@click.option(
    "--token-file",
    default=OWNER_TOKEN_FILENAME,
    show_default=True,
    help="Saved owner token file, relative to the project root.",
)
@click.option("--force", is_flag=True, help="Overwrite an existing local .api_key.")
@click.pass_context
def register_agent(
    ctx,
    name,
    backend,
    description,
    github_repo,
    owner_token,
    email,
    password,
    token_file,
    force,
):
    """Register a local agent on Koala and save its one-time API key."""
    cfg = _get_config(ctx)
    repo = github_repo or cfg.github_repo
    repo_err = validate_github_repo(repo)
    if repo_err:
        raise click.ClickException(repo_err)

    agent_dir = cfg.agents_dir / name
    if not agent_dir.exists():
        agent_dir = _create_agent_files(cfg, name=name, backend=backend)
        click.echo(f"Created local agent: {agent_dir}")

    api_key_path = agent_dir / ".api_key"
    if api_key_path.exists() and api_key_path.read_text(encoding="utf-8").strip() and not force:
        raise click.ClickException(
            f"{api_key_path} already exists. Use --force only if you are replacing it intentionally."
        )

    token = _resolve_owner_token(
        cfg,
        owner_token=owner_token,
        token_file=token_file,
        email=email,
        password=password,
    )
    profile_description = description or _default_agent_description(agent_dir, name)
    try:
        result = register_koala_agent(
            owner_token=token,
            name=name,
            github_repo=repo,
            description=profile_description,
            base_url=cfg.koala_base_url,
        )
    except KoalaApiError as exc:
        raise click.ClickException(str(exc))

    save_agent_credentials(agent_dir, agent_id=result["id"], api_key=result["api_key"])
    click.echo(f"Registered agent: {name} ({result['id']})")
    click.echo(f"  key: {api_key_path}")
    click.echo(f"  repo: {repo}")


@main.command(name="agents")
@click.option("--owner-token", default=None, help="Koala human owner access token.")
@click.option(
    "--token-file",
    default=OWNER_TOKEN_FILENAME,
    show_default=True,
    help="Saved owner token file, relative to the project root.",
)
@click.pass_context
def agents(ctx, owner_token, token_file):
    """List Koala agents registered under the saved owner token."""
    cfg = _get_config(ctx)
    token = _resolve_owner_token(cfg, owner_token=owner_token, token_file=token_file)
    try:
        rows = list_registered_agents(owner_token=token, base_url=cfg.koala_base_url)
    except KoalaApiError as exc:
        raise click.ClickException(str(exc))
    if not rows:
        click.echo("No registered agents.")
        return
    click.echo(f"{'NAME':<28s} {'KARMA':>8s} {'STRIKES':>7s} {'ID'}")
    click.echo("-" * 80)
    for row in rows:
        click.echo(
            f"{row['name']:<28s} {row['karma']:>8.1f} "
            f"{row['strike_count']:>7d} {row['id']}"
        )


# --------------------------------------------------------------------------- #
# reva launch
# --------------------------------------------------------------------------- #


@main.command()
@click.option("--name", required=True, help="Agent name to launch.")
@click.option("--duration", type=float, default=None, help="Hours to run (omit for indefinite; ignored with --cluster).")
@click.option("--backend", type=click.Choice(BACKEND_CHOICES), default=None, help="Override backend.")
@click.option(
    "--session-timeout",
    type=int,
    default=600,
    help="Max seconds per invocation before restart (default: 600).",
)
@click.option(
    "--cluster",
    is_flag=True,
    help="Submit as a SLURM sbatch job instead of running in tmux.",
)
@click.option(
    "--partition",
    default="main-cpu",
    show_default=True,
    help="SLURM partition (--cluster only).",
)
@click.option(
    "--time",
    "time",
    default="5-00:00:00",
    show_default=True,
    help="SLURM wall time (--cluster only), e.g. 5-00:00:00.",
)
@click.option(
    "--cpus",
    type=int,
    default=4,
    show_default=True,
    help="SLURM --cpus-per-task (--cluster only).",
)
@click.option(
    "--mem",
    default="16G",
    show_default=True,
    help="SLURM --mem (--cluster only).",
)
@click.option(
    "--max-chain",
    type=int,
    default=3,
    show_default=True,
    help="Max sbatch jobs chained via the wall-time trap (--cluster only).",
)
@click.pass_context
def launch(ctx, name, duration, backend, session_timeout, cluster, partition, time, cpus, mem, max_chain):
    """Launch an agent in a tmux session (default) or as a SLURM job (--cluster)."""
    cfg = _get_config(ctx)
    agent_dir = cfg.agents_dir / name
    if not agent_dir.exists():
        raise click.ClickException(f"Agent not found: {agent_dir}")

    if os.environ.get("REVA_ALLOW_UPSTREAM_REPO", "").strip().lower() not in ("1", "true", "yes"):
        repo_err = validate_github_repo(cfg.github_repo)
        if repo_err:
            raise click.ClickException(repo_err)

    api_key_path = agent_dir / ".api_key"
    if not api_key_path.exists() or not api_key_path.read_text(encoding="utf-8").strip():
        raise click.ClickException(
            f".api_key missing — ask the owner to provision it at "
            f"{cfg.koala_base_url}/owners and drop the key at {api_key_path}"
        )

    agent_config = json.loads((agent_dir / "config.json").read_text())
    backend_name = backend or agent_config["backend"]
    backend_obj = get_backend(backend_name)

    prompt = assemble_prompt(
        global_rules_path=cfg.global_rules_path,
        platform_skills_path=cfg.platform_skills_path,
        agent_prompt_path=agent_dir / "system_prompt.md",
    )
    (agent_dir / "prompt.md").write_text(prompt, encoding="utf-8")
    (agent_dir / backend_obj.prompt_filename).write_text(prompt, encoding="utf-8")

    initial_prompt = DEFAULT_INITIAL_PROMPT.format(koala_base_url=cfg.koala_base_url)
    (agent_dir / "initial_prompt.txt").write_text(initial_prompt, encoding="utf-8")

    escaped_prompt = initial_prompt.replace('"', '\\"')
    cmd = backend_obj.command_template.format(prompt=escaped_prompt)

    resume_cmd = (
        backend_obj.resume_command_template.format(prompt=escaped_prompt)
        if backend_obj.resume_command_template is not None
        else None
    )

    if cluster:
        script = build_launch_script(
            cmd,
            duration_hours=None,
            session_timeout=session_timeout,
            resume_command=resume_cmd,
            session_id_extractor=backend_obj.session_id_extractor,
        )
        write_launch_files(str(agent_dir), script)
        try:
            job_id = submit_agent(
                str(agent_dir),
                agent_name=name,
                partition=partition,
                time=time,
                cpus=cpus,
                mem=mem,
                max_chain=max_chain,
            )
        except (RuntimeError, ValueError, FileNotFoundError) as exc:
            raise click.ClickException(str(exc))
        click.echo(f"Submitted job {job_id} for agent {name} (chain 1/{max_chain})")
        click.echo(f"  SLURM job-name: reva_{name}")
        click.echo(f"  logs: {agent_dir / 'agent.log'}")
        return

    script = build_launch_script(
        cmd,
        duration_hours=duration,
        session_timeout=session_timeout,
        resume_command=resume_cmd,
        session_id_extractor=backend_obj.session_id_extractor,
    )
    create_session(name, str(agent_dir), script)

    dur_str = f"{duration}h" if duration else "indefinite"
    click.echo(f"Launched: {name} ({backend_name}, {dur_str})")
    click.echo(f"  tmux session: reva_{name}")
    click.echo(f"  attach: tmux attach -t reva_{name}")


# --------------------------------------------------------------------------- #
# reva stop
# --------------------------------------------------------------------------- #


@main.command()
@click.option("--name", default=None, help="Agent name to stop.")
@click.option("--all", "kill_all", is_flag=True, help="Stop all running agents.")
@click.option("--cluster", is_flag=True, help="Cancel SLURM chain(s) instead of tmux session(s).")
@click.pass_context
def stop(ctx, name, kill_all, cluster):
    """Stop a running agent (kill its tmux session or cancel its SLURM chain)."""
    if cluster:
        cfg = _get_config(ctx)
        if kill_all:
            jobs = list_cluster_jobs()
            agents = sorted({j.agent_name for j in jobs})
            total = 0
            for agent_name in agents:
                total += cancel_chain(agent_name=agent_name, agent_dir=str(cfg.agents_dir / agent_name))
            click.echo(f"Cancelled {total} SLURM job(s) across {len(agents)} agent(s).")
        elif name:
            count = cancel_chain(agent_name=name, agent_dir=str(cfg.agents_dir / name))
            click.echo(f"Cancelled {count} SLURM job(s) for: {name}")
        else:
            raise click.ClickException("Provide --name or --all.")
        return

    if kill_all:
        count = kill_all_sessions()
        click.echo(f"Stopped {count} agent(s).")
    elif name:
        if kill_session(name):
            click.echo(f"Stopped: {name}")
        else:
            click.echo(f"No running session for: {name}")
    else:
        raise click.ClickException("Provide --name or --all.")


# hidden alias so `reva kill` still works
_kill = click.Command(name="kill", callback=stop.callback, params=stop.params, help=stop.help, hidden=True)
main.add_command(_kill)


# --------------------------------------------------------------------------- #
# reva delete
# --------------------------------------------------------------------------- #


@main.command()
@click.argument("names", nargs=-1, required=True)
@click.option("--force", is_flag=True, help="Skip confirmation.")
@click.pass_context
def delete(ctx, names, force):
    """Remove agent directories (kills running sessions first)."""
    cfg = _get_config(ctx)
    for name in names:
        agent_dir = cfg.agents_dir / name
        if not agent_dir.exists():
            click.echo(f"Not found: {name}")
            continue
        if not force:
            click.confirm(f"Delete {agent_dir}?", abort=True)
        if has_session(name):
            kill_session(name)
        shutil.rmtree(agent_dir)
        click.echo(f"Deleted: {name}")


# --------------------------------------------------------------------------- #
# reva status
# --------------------------------------------------------------------------- #


@main.command()
@click.pass_context
def status(ctx):
    """List running agents (tmux sessions and SLURM cluster jobs)."""
    sessions = list_sessions()
    jobs = list_cluster_jobs()

    if not sessions and not jobs:
        click.echo("No running agents.")
        return

    cfg = _get_config(ctx)

    def _backend_for(agent_name: str) -> str:
        agent_config_path = cfg.agents_dir / agent_name / "config.json"
        if agent_config_path.exists():
            return json.loads(agent_config_path.read_text()).get("backend", "?")
        return "?"

    click.echo(f"{'NAME':<24s} {'BACKEND':<12s} {'MODE':<6s} {'JOB/SESSION':<20s} {'STATE'}")
    click.echo("-" * 78)
    for s in sessions:
        click.echo(
            f"{s.agent_name:<24s} {_backend_for(s.agent_name):<12s} "
            f"{'tmux':<6s} {s.session:<20s} RUNNING"
        )
    for j in jobs:
        click.echo(
            f"{j.agent_name:<24s} {_backend_for(j.agent_name):<12s} "
            f"{'slurm':<6s} {str(j.job_id):<20s} {j.state}"
        )


# --------------------------------------------------------------------------- #
# reva log
# --------------------------------------------------------------------------- #


@main.command(name="log")
@click.argument("name", required=False)
@click.option("--all", "watch_all", is_flag=True, help="Interleave all running agents.")
@click.pass_context
def log(ctx, name, watch_all):
    """Stream a readable live view of agent activity (ATIF-backed)."""
    from reva.render import render_step_terminal
    from reva.session import SessionContext

    cfg = _get_config(ctx)

    if watch_all:
        agents = sorted(d for d in cfg.agents_dir.iterdir() if d.is_dir() and (d / "agent.log").exists())
        if not agents:
            raise click.ClickException("No agent logs found.")
        log_files = [(a.name, a / "agent.log") for a in agents]
    elif name:
        agent_dir = cfg.agents_dir / name
        log_file = agent_dir / "agent.log"
        if not log_file.exists():
            raise click.ClickException(f"No agent.log found for: {name}")
        log_files = [(name, log_file)]
    else:
        agents = sorted(
            (d for d in cfg.agents_dir.iterdir() if d.is_dir() and (d / "agent.log").exists()),
            key=lambda d: (d / "agent.log").stat().st_mtime,
            reverse=True,
        )
        if not agents:
            raise click.ClickException("No agent logs found.")
        log_files = [(agents[0].name, agents[0] / "agent.log")]
        click.echo(f"Watching: {agents[0].name}\n")

    handles = {n: open(p, "r") for n, p in log_files}
    contexts = {n: SessionContext.for_agent(cfg.agents_dir / n) for n, _ in log_files}
    prefix = len(log_files) > 1

    try:
        while True:
            activity = False
            for agent_name, fh in handles.items():
                line = fh.readline()
                if not line:
                    continue
                activity = True
                sess = contexts[agent_name]
                for step in sess.consume_lines([line]):
                    for rendered in render_step_terminal(step, agent_name if prefix else None):
                        click.echo(rendered)
            if not activity:
                for agent_name, sess in contexts.items():
                    for step in sess.flush_pending():
                        for rendered in render_step_terminal(step, agent_name if prefix else None):
                            click.echo(rendered)
                    try:
                        sess.flush()
                    except Exception:
                        pass
                time.sleep(0.2)
    except KeyboardInterrupt:
        pass
    finally:
        for fh in handles.values():
            fh.close()
        for sess in contexts.values():
            try:
                sess.flush()
            except Exception:
                pass


# hidden alias so `reva watch` still works
_watch = click.Command(name="watch", callback=log.callback, params=log.params, help=log.help, hidden=True)
main.add_command(_watch)


# --------------------------------------------------------------------------- #
# reva view
# --------------------------------------------------------------------------- #


@main.command()
@click.option("--web", is_flag=True, help="Serve an interactive web UI instead of the TUI.")
@click.option("--host", default="127.0.0.1", show_default=True, help="Web host (with --web).")
@click.option("--port", default=8765, show_default=True, type=int, help="Web port (with --web).")
@click.pass_context
def view(ctx, web, host, port):
    """Launch the interactive ATIF viewer (TUI, or web with --web)."""
    cfg = _get_config(ctx)
    if web:
        from reva.web import serve

        serve(cfg, host=host, port=port)
        return
    from reva.viewer import RevaViewer

    app = RevaViewer(cfg=cfg)
    app.run()


# --------------------------------------------------------------------------- #
# reva research
# --------------------------------------------------------------------------- #


def _project_path(cfg, value, default):
    raw = Path(value or default)
    return raw if raw.is_absolute() else (cfg.project_root / raw)


@main.group()
def research():
    """Run offline autoresearch loops for prompt variants."""


@research.command("run")
@click.option("--name", required=True, help="Agent name to evaluate.")
@click.option(
    "--tasks",
    default=None,
    help="JSONL task file. Defaults to research/tasks/smoke.jsonl.",
)
@click.option(
    "--variants-dir",
    default=None,
    help="Directory of .md prompt variants. Defaults to research/variants.",
)
@click.option(
    "--output-dir",
    default=None,
    help="Directory for run outputs. Defaults to research/runs.",
)
@click.option("--iterations", type=int, default=1, show_default=True)
@click.option("--top-k", type=int, default=2, show_default=True)
@click.option(
    "--runner",
    default=None,
    help=(
        "Optional external command. Supports {prompt_file}, {task_file}, "
        "and {output_file} placeholders. Without this, uses a deterministic mock runner."
    ),
)
@click.option("--runner-shell", is_flag=True, help="Run --runner through the shell.")
@click.option("--retries", type=int, default=0, show_default=True, help="Retries per candidate.")
@click.option("--fail-fast", is_flag=True, help="Abort the run on the first candidate failure.")
@click.option("--timeout", type=int, default=300, show_default=True, help="Runner timeout in seconds.")
@click.pass_context
def research_run(
    ctx,
    name,
    tasks,
    variants_dir,
    output_dir,
    iterations,
    top_k,
    runner,
    runner_shell,
    retries,
    fail_fast,
    timeout,
):
    """Evaluate prompt variants offline without posting to Koala."""
    from reva.research import run_research

    cfg = _get_config(ctx)
    agent_dir = cfg.agents_dir / name
    if not agent_dir.exists():
        raise click.ClickException(f"Agent not found: {agent_dir}")

    try:
        run_dir = run_research(
            agent_dir=agent_dir,
            tasks_path=_project_path(cfg, tasks, "research/tasks/smoke.jsonl"),
            variants_dir=_project_path(cfg, variants_dir, "research/variants"),
            output_root=_project_path(cfg, output_dir, "research/runs"),
            runner_command=runner,
            runner_shell=runner_shell,
            retries=retries,
            fail_fast=fail_fast,
            iterations=iterations,
            top_k=top_k,
            timeout_seconds=timeout,
        )
    except (OSError, RuntimeError, ValueError) as exc:
        raise click.ClickException(str(exc))

    click.echo(f"Research run written to: {run_dir}")
    click.echo(f" report: {run_dir / 'report.md'}")
    click.echo(f" scores: {run_dir / 'scores.json'}")


@research.command("promote")
@click.option("--name", required=True, help="Agent name to update.")
@click.option("--run-dir", required=True, help="Research run directory containing scores.json.")
@click.option("--variant", "variant_id", default=None, help="Variant id to promote. Defaults to best.")
@click.pass_context
def research_promote(ctx, name, run_dir, variant_id):
    """Append the best research variant to an agent's system prompt."""
    from reva.research import promote_variant

    cfg = _get_config(ctx)
    agent_dir = cfg.agents_dir / name
    if not agent_dir.exists():
        raise click.ClickException(f"Agent not found: {agent_dir}")

    resolved_run_dir = _project_path(cfg, run_dir, run_dir)
    try:
        result = promote_variant(
            agent_dir=agent_dir,
            run_dir=resolved_run_dir,
            variant_id=variant_id,
        )
    except (OSError, ValueError) as exc:
        raise click.ClickException(str(exc))

    click.echo(f"Promoted variant: {result['variant_id']}")
    click.echo(f" prompt: {result['prompt_path']}")
    click.echo(f" backup: {result['backup_path']}")
    click.echo(f" mean total: {result['mean_total']:.4f}")


# --------------------------------------------------------------------------- #
# reva archive / unarchive
# --------------------------------------------------------------------------- #


@main.command()
@click.option("--name", default=None, help="Agent name to archive.")
@click.option("--list", "list_archived", is_flag=True, help="List archived agents.")
@click.pass_context
def archive(ctx, name, list_archived):
    """Archive (retire) an agent by moving it to .archived/."""
    cfg = _get_config(ctx)
    archived_dir = cfg.agents_dir / ".archived"

    if list_archived:
        if not archived_dir.exists():
            click.echo("No archived agents.")
            return
        agents = sorted(
            d for d in archived_dir.iterdir()
            if d.is_dir() and (d / "config.json").exists()
        )
        if not agents:
            click.echo("No archived agents.")
            return
        for a in agents:
            click.echo(f"  {a.name}")
        click.echo(f"\n{len(agents)} archived agent(s)")
        return

    if not name:
        raise click.ClickException("Provide --name or --list.")

    agent_dir = cfg.agents_dir / name
    if not agent_dir.exists():
        raise click.ClickException(f"Agent not found: {name}")

    if has_session(name):
        kill_session(name)
        click.echo(f"Killed running session for: {name}")

    archived_dir.mkdir(parents=True, exist_ok=True)
    dest = archived_dir / name
    if dest.exists():
        raise click.ClickException(f"Already archived: {name}")
    shutil.move(str(agent_dir), str(dest))
    click.echo(f"Archived agent: {name}")


@main.command()
@click.option("--name", required=True, help="Agent name to unarchive.")
@click.pass_context
def unarchive(ctx, name):
    """Unarchive (restore) an agent from .archived/ back to agents_dir."""
    cfg = _get_config(ctx)
    archived_dir = cfg.agents_dir / ".archived"
    src = archived_dir / name
    if not src.exists():
        raise click.ClickException(f"Agent '{name}' is not archived.")

    dest = cfg.agents_dir / name
    if dest.exists():
        raise click.ClickException(f"Agent already exists at: {dest}")

    shutil.move(str(src), str(dest))
    click.echo(f"Unarchived agent: {name}")


if __name__ == "__main__":
    main()
