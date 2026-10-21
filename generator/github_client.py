from __future__ import annotations

import json
from collections import defaultdict
from collections.abc import Callable
from typing import Any, TypeAlias
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from generator.models import PublicProfileData, RepositoryData


class GitHubApiError(RuntimeError):
    """Raised when public profile data cannot be read safely."""


JsonRequester: TypeAlias = Callable[
    [str, dict[str, object], str], dict[str, object]
]

_GRAPHQL_URL = "https://api.github.com/graphql"
_PROFILE_QUERY = """
query PublicProfile($login: String!) {
  user(login: $login) {
    followers { totalCount }
    contributionsCollection {
      contributionCalendar { totalContributions }
    }
    repositories(
      first: 100
      ownerAffiliations: OWNER
      privacy: PUBLIC
      orderBy: {field: UPDATED_AT, direction: DESC}
    ) {
      nodes {
        name
        url
        description
        isFork
        isPrivate
        visibility
        primaryLanguage { name }
        languages(first: 20, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
      }
    }
  }
}
""".strip()


def _default_request_json(
    query: str,
    variables: dict[str, object],
    token: str,
) -> dict[str, object]:
    body = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    request = Request(
        _GRAPHQL_URL,
        data=body,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "nicolas-takimo-profile-generator",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise GitHubApiError(f"GitHub GraphQL API request failed: {exc}") from exc
    if not isinstance(payload, dict):
        raise GitHubApiError("GitHub GraphQL API returned a non-object response")
    return payload


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


def _repository(node: dict[str, Any]) -> RepositoryData | None:
    if node.get("isFork") is not False:
        return None
    if node.get("isPrivate") is not False or node.get("visibility") != "PUBLIC":
        return None
    name = node.get("name")
    url = node.get("url")
    if not isinstance(name, str) or not name or not isinstance(url, str) or not url:
        return None

    description = node.get("description")
    if not isinstance(description, str):
        description = None
    primary_language_data = node.get("primaryLanguage")
    primary_language = None
    if isinstance(primary_language_data, dict):
        value = primary_language_data.get("name")
        if isinstance(value, str) and value:
            primary_language = value

    language_bytes: dict[str, int] = {}
    languages = node.get("languages")
    edges = languages.get("edges", []) if isinstance(languages, dict) else []
    if isinstance(edges, list):
        for edge in edges:
            if not isinstance(edge, dict):
                continue
            language_node = edge.get("node")
            language = language_node.get("name") if isinstance(language_node, dict) else None
            size = edge.get("size")
            if isinstance(language, str) and isinstance(size, int) and not isinstance(size, bool):
                language_bytes[language] = max(0, size)

    return RepositoryData(
        name=name,
        url=url,
        description=description,
        primary_language=primary_language,
        language_bytes=language_bytes,
    )


def fetch_public_profile(
    username: str,
    token: str,
    request_json: JsonRequester | None = None,
) -> PublicProfileData:
    requester = request_json or _default_request_json
    try:
        payload = requester(_PROFILE_QUERY, {"login": username}, token)
    except GitHubApiError:
        raise
    except Exception as exc:
        raise GitHubApiError(f"GitHub GraphQL API request failed: {exc}") from exc

    if not isinstance(payload, dict):
        raise GitHubApiError("GitHub GraphQL API returned a malformed payload")
    if payload.get("errors"):
        raise GitHubApiError("GitHub GraphQL API returned errors")
    data = payload.get("data")
    user = data.get("user") if isinstance(data, dict) else None
    if not isinstance(user, dict):
        raise GitHubApiError("GitHub GraphQL API did not return the requested user")

    followers_data = user.get("followers")
    followers = _optional_int(
        followers_data.get("totalCount") if isinstance(followers_data, dict) else None
    )
    contributions_data = user.get("contributionsCollection")
    calendar = (
        contributions_data.get("contributionCalendar")
        if isinstance(contributions_data, dict)
        else None
    )
    contributions = _optional_int(
        calendar.get("totalContributions") if isinstance(calendar, dict) else None
    )

    repositories_data = user.get("repositories")
    nodes = repositories_data.get("nodes") if isinstance(repositories_data, dict) else []
    repositories: dict[str, RepositoryData] = {}
    totals: defaultdict[str, int] = defaultdict(int)
    if isinstance(nodes, list):
        for raw_node in nodes:
            if not isinstance(raw_node, dict):
                continue
            repository = _repository(raw_node)
            if repository is None:
                continue
            repositories[repository.name] = repository
            for language, size in repository.language_bytes.items():
                totals[language] += size

    language_bytes = dict(totals)
    return PublicProfileData(
        username=username,
        public_repository_count=len(repositories),
        contributions_year=contributions,
        followers=followers,
        language_count=len(language_bytes),
        language_bytes=language_bytes,
        repositories=repositories,
    )
