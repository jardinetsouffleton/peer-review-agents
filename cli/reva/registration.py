"""Koala owner and agent registration helpers."""

from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import certifi

from reva.env import koala_base_url

OWNER_TOKEN_FILENAME = ".reva_owner_token"


class KoalaApiError(RuntimeError):
    """Raised when the Koala API returns a non-2xx response."""


def api_base_url(base_url: str | None = None) -> str:
    base = (base_url or koala_base_url()).rstrip("/")
    if base.endswith("/api/v1"):
        return base
    return f"{base}/api/v1"


def signup_owner(
    *,
    email: str,
    password: str,
    name: str,
    openreview_ids: list[str],
    base_url: str | None = None,
) -> dict[str, Any]:
    return _request_json(
        "POST",
        "/auth/signup",
        {
            "email": email,
            "password": password,
            "name": name,
            "openreview_ids": openreview_ids,
        },
        base_url=base_url,
    )


def login_owner(
    *,
    email: str,
    password: str,
    base_url: str | None = None,
) -> dict[str, Any]:
    return _request_json(
        "POST",
        "/auth/login",
        {"email": email, "password": password},
        base_url=base_url,
    )


def create_agent(
    *,
    owner_token: str,
    name: str,
    github_repo: str,
    description: str | None = None,
    base_url: str | None = None,
) -> dict[str, Any]:
    payload = {"name": name, "github_repo": github_repo}
    if description:
        payload["description"] = description
    return _request_json(
        "POST",
        "/auth/agents",
        payload,
        owner_token=owner_token,
        base_url=base_url,
    )


def list_agents(*, owner_token: str, base_url: str | None = None) -> list[dict[str, Any]]:
    return _request_json(
        "GET",
        "/auth/agents",
        None,
        owner_token=owner_token,
        base_url=base_url,
    )


def save_owner_token(path: Path, token: str) -> None:
    path.write_text(token.strip() + "\n", encoding="utf-8")
    path.chmod(0o600)


def read_owner_token(path: Path) -> str | None:
    if not path.exists():
        return None
    token = path.read_text(encoding="utf-8").strip()
    return token or None


def save_agent_credentials(agent_dir: Path, *, agent_id: str, api_key: str) -> None:
    api_key_path = agent_dir / ".api_key"
    api_key_path.write_text(api_key.strip() + "\n", encoding="utf-8")
    api_key_path.chmod(0o600)
    (agent_dir / ".agent_id").write_text(agent_id.strip() + "\n", encoding="utf-8")


def split_openreview_ids(values: tuple[str, ...]) -> list[str]:
    result: list[str] = []
    for value in values:
        for part in value.split(","):
            stripped = part.strip()
            if stripped:
                result.append(stripped)
    return result


def _request_json(
    method: str,
    path: str,
    payload: dict[str, Any] | None,
    *,
    owner_token: str | None = None,
    base_url: str | None = None,
) -> Any:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Accept": "application/json"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if owner_token:
        headers["Authorization"] = f"Bearer {owner_token.strip()}"

    request = urllib.request.Request(
        f"{api_base_url(base_url)}{path}",
        data=data,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=30, context=_ssl_context()) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise KoalaApiError(_format_http_error(exc)) from exc
    except urllib.error.URLError as exc:
        raise KoalaApiError(f"Koala API request failed: {exc.reason}") from exc

    if not body.strip():
        return {}
    return json.loads(body)


def _format_http_error(exc: urllib.error.HTTPError) -> str:
    raw = exc.read().decode("utf-8", errors="replace")
    detail = raw
    try:
        parsed = json.loads(raw)
        detail = parsed.get("detail") or parsed.get("message") or raw
    except json.JSONDecodeError:
        pass
    return f"Koala API returned {exc.code}: {detail}"


def _ssl_context() -> ssl.SSLContext:
    return ssl.create_default_context(cafile=certifi.where())
