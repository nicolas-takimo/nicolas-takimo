from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True, slots=True)
class Identity:
    username: str
    name: str
    title_en: str
    subtitle_pt: str
    company: str
    location: str
    email: str | None = None
    linkedin_url: str | None = None
    portfolio_url: str | None = None


@dataclass(frozen=True, slots=True)
class Domain:
    name: str
    color: str


@dataclass(frozen=True, slots=True)
class Technology:
    name: str
    domain: str


@dataclass(frozen=True, slots=True)
class FeaturedProject:
    repository: str
    domain: str
    description_en: str
    description_pt: str


@dataclass(frozen=True, slots=True)
class Palette:
    background: str
    surface: str
    text: str
    muted: str
    cyan: str
    violet: str
    green: str
    amber: str


@dataclass(frozen=True, slots=True)
class ProfileConfig:
    identity: Identity
    domains: tuple[Domain, ...]
    technologies: tuple[Technology, ...]
    featured_projects: tuple[FeaturedProject, ...]
    palette: Palette


@dataclass(frozen=True, slots=True)
class RepositoryData:
    name: str
    url: str
    description: str | None
    primary_language: str | None
    language_bytes: Mapping[str, int]


@dataclass(frozen=True, slots=True)
class PublicProfileData:
    username: str
    public_repository_count: int
    contributions_year: int | None
    followers: int | None
    language_count: int
    language_bytes: Mapping[str, int]
    repositories: Mapping[str, RepositoryData]
