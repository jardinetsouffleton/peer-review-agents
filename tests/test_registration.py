import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from reva.registration import (
    api_base_url,
    read_owner_token,
    save_agent_credentials,
    save_owner_token,
    split_openreview_ids,
)


def test_api_base_url_appends_api_v1():
    assert api_base_url("https://koala.science") == "https://koala.science/api/v1"


def test_api_base_url_does_not_duplicate_api_v1():
    assert api_base_url("https://koala.science/api/v1") == "https://koala.science/api/v1"


def test_split_openreview_ids_accepts_repeated_and_comma_separated_values():
    assert split_openreview_ids(("~A_B1, ~C_D1", "~E_F1")) == [
        "~A_B1",
        "~C_D1",
        "~E_F1",
    ]


def test_save_and_read_owner_token(tmp_path):
    path = tmp_path / ".reva_owner_token"
    save_owner_token(path, "TOKEN")
    assert read_owner_token(path) == "TOKEN"
    assert not (path.stat().st_mode & 0o077)


def test_save_agent_credentials(tmp_path):
    save_agent_credentials(tmp_path, agent_id="agent-id", api_key="cs_key")
    assert (tmp_path / ".api_key").read_text(encoding="utf-8").strip() == "cs_key"
    assert (tmp_path / ".agent_id").read_text(encoding="utf-8").strip() == "agent-id"
    assert not ((tmp_path / ".api_key").stat().st_mode & 0o077)


def test_create_agent_posts_bearer_owner_token():
    from reva.registration import create_agent

    response = MagicMock()
    response.__enter__.return_value.read.return_value = json.dumps(
        {"id": "agent-id", "api_key": "cs_key"}
    ).encode("utf-8")

    with patch("reva.registration.urllib.request.urlopen", return_value=response) as mock_open:
        result = create_agent(
            owner_token="OWNER",
            name="alpha",
            github_repo="https://github.com/example/repo",
            description="Rigor reviewer",
            base_url="https://koala.science",
        )

    request = mock_open.call_args.args[0]
    assert request.full_url == "https://koala.science/api/v1/auth/agents"
    assert request.get_method() == "POST"
    assert request.headers["Authorization"] == "Bearer OWNER"
    assert result["api_key"] == "cs_key"
