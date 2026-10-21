import json
from copy import deepcopy
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
