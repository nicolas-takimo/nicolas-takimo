import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

import pytest

from generator.github_client import GitHubApiError, fetch_public_profile


FIXTURES = Path(__file__).with_name("fixtures")


def _fixture(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_fetch_public_profile_normalizes_public_non_fork_data():
    payload = _fixture("github-profile.json")

    profile = fetch_public_profile(
        "nicolas-takimo",
        "test-token",
        request_json=lambda _query, _variables, _token: payload,
    )

    assert profile.public_repository_count == 2
    assert set(profile.repositories) == {"gavioes-style-fluxos", "cyberSolana"}
    assert profile.repositories["gavioes-style-fluxos"].primary_language == "TypeScript"
    assert profile.contributions_year == 58
    assert profile.followers == 14
    assert profile.language_count == 3
    assert profile.language_bytes == {"TypeScript": 740, "CSS": 80, "Python": 400}


def test_fetch_public_profile_preserves_missing_metrics_as_none():
    payload = _fixture("github-profile-partial.json")

    profile = fetch_public_profile(
        "nicolas-takimo",
        "test-token",
        request_json=lambda _query, _variables, _token: payload,
    )

    assert profile.contributions_year is None
    assert profile.followers is None
    assert profile.language_count == 0
    assert profile.repositories["project-with-missing-fields"].description is None
    assert profile.repositories["project-with-missing-fields"].primary_language is None


def test_fetch_public_profile_requests_current_calendar_year():
    payload = _fixture("github-profile.json")
    captured = {}

    def request(query, variables, _token):
        captured["query"] = query
        captured["variables"] = variables
        return payload

    fetch_public_profile(
        "nicolas-takimo",
        "test-token",
        request_json=request,
        now=datetime(2027, 1, 1, 0, 0, 1, tzinfo=timezone.utc),
    )

    assert "contributionsCollection(from: $from, to: $to)" in captured["query"]
    assert captured["variables"] == {
        "login": "nicolas-takimo",
        "from": "2027-01-01T00:00:00Z",
        "to": "2027-01-01T00:00:01Z",
    }


@pytest.mark.parametrize("repository_value", [None, "absent"])
def test_fetch_public_profile_preserves_unavailable_repositories_as_none(repository_value):
    payload = deepcopy(_fixture("github-profile.json"))
    user = payload["data"]["user"]
    if repository_value == "absent":
        del user["repositories"]
    else:
        user["repositories"] = repository_value

    profile = fetch_public_profile(
        "nicolas-takimo",
        "test-token",
        request_json=lambda _query, _variables, _token: payload,
    )

    assert profile.public_repository_count is None
    assert profile.language_count is None
    assert profile.language_bytes is None


@pytest.mark.parametrize("language_value", [None, "absent"])
def test_fetch_public_profile_preserves_unavailable_languages_as_none(language_value):
    payload = deepcopy(_fixture("github-profile.json"))
    repository = payload["data"]["user"]["repositories"]["nodes"][0]
    if language_value == "absent":
        del repository["languages"]
    else:
        repository["languages"] = language_value

    profile = fetch_public_profile(
        "nicolas-takimo",
        "test-token",
        request_json=lambda _query, _variables, _token: payload,
    )

    assert profile.repositories["gavioes-style-fluxos"].language_bytes is None
    assert profile.language_count is None
    assert profile.language_bytes is None


def test_fetch_public_profile_excludes_private_and_fork_nodes():
    payload = deepcopy(_fixture("github-profile.json"))
    private_repo = deepcopy(payload["data"]["user"]["repositories"]["nodes"][0])
    private_repo.update(
        name="private-project",
        isPrivate=True,
        visibility="PRIVATE",
    )
    payload["data"]["user"]["repositories"]["nodes"].append(private_repo)

    profile = fetch_public_profile(
        "nicolas-takimo",
        "test-token",
        request_json=lambda _query, _variables, _token: payload,
    )

    assert "private-project" not in profile.repositories
    assert "forked-project" not in profile.repositories
    assert profile.public_repository_count == 2


def test_fetch_public_profile_raises_on_graphql_errors():
    token = "token-must-not-leak"

    with pytest.raises(GitHubApiError, match="GitHub GraphQL API") as caught:
        fetch_public_profile(
            "nicolas-takimo",
            token,
            request_json=lambda _query, _variables, _token: {
                "errors": [{"message": "rate limit exceeded"}]
            },
        )

    assert token not in str(caught.value)


def test_fetch_public_profile_raises_on_malformed_payload():
    with pytest.raises(GitHubApiError, match="GitHub GraphQL API"):
        fetch_public_profile(
            "nicolas-takimo",
            "test-token",
            request_json=lambda _query, _variables, _token: {"data": {"user": None}},
        )
