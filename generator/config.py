from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from generator.models import (
    Domain,
    FeaturedProject,
    Identity,
    Palette,
    ProfileConfig,
    Technology,
)


class ConfigError(ValueError):
    """Raised when the curated profile configuration is invalid."""


_HEX_COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")
_IDENTITY_KEYS = {
    "username",
    "name",
    "title_en",
    "subtitle_pt",
    "company",
    "location",
    "email",
    "linkedin_url",
    "portfolio_url",
}
_PROJECT_KEYS = {
    "repository",
    "domain",
    "description_en",
    "description_pt",
}
_PALETTE_KEYS = {
    "background",
    "surface",
    "text",
    "muted",
    "cyan",
    "violet",
    "green",
    "amber",
}


def _mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ConfigError(f"{field} must be a mapping")
    return value


def _list(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise ConfigError(f"{field} must be a list")
    return value


def _required_text(data: dict[str, Any], key: str, field: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{field}.{key} must be non-empty text")
    return value.strip()


def _optional_text(data: dict[str, Any], key: str, field: str) -> str | None:
    value = data.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{field}.{key} must be text or null")
    return value.strip()


def _unknown_keys(data: dict[str, Any], allowed: set[str], field: str) -> None:
    unknown = set(data) - allowed
    if unknown:
        key = sorted(unknown)[0]
        raise ConfigError(f"{field}.{key} is not supported")


def load_config(path: Path) -> ProfileConfig:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ConfigError(f"config: {exc}") from exc

    root = _mapping(raw, "config")
    if "identity" not in root:
        raise ConfigError("identity is required")

    identity_data = _mapping(root["identity"], "identity")
    _unknown_keys(identity_data, _IDENTITY_KEYS, "identity")
    identity = Identity(
        username=_required_text(identity_data, "username", "identity"),
        name=_required_text(identity_data, "name", "identity"),
        title_en=_required_text(identity_data, "title_en", "identity"),
        subtitle_pt=_required_text(identity_data, "subtitle_pt", "identity"),
        company=_required_text(identity_data, "company", "identity"),
        location=_required_text(identity_data, "location", "identity"),
        email=_optional_text(identity_data, "email", "identity"),
        linkedin_url=_optional_text(identity_data, "linkedin_url", "identity"),
        portfolio_url=_optional_text(identity_data, "portfolio_url", "identity"),
    )

    domains: list[Domain] = []
    seen_domains: set[str] = set()
    for index, item in enumerate(_list(root.get("domains"), "domains")):
        domain_data = _mapping(item, f"domains[{index}]")
        _unknown_keys(domain_data, {"name", "color"}, f"domains[{index}]")
        name = _required_text(domain_data, "name", f"domains[{index}]")
        color = _required_text(domain_data, "color", f"domains[{index}]")
        if name in seen_domains:
            raise ConfigError(f"domains contains duplicate name: {name}")
        if not _HEX_COLOR.fullmatch(color):
            raise ConfigError(f"domains[{index}].color must be #RRGGBB")
        seen_domains.add(name)
        domains.append(Domain(name=name, color=color.upper()))

    technologies: list[Technology] = []
    for index, item in enumerate(_list(root.get("technologies"), "technologies")):
        tech_data = _mapping(item, f"technologies[{index}]")
        _unknown_keys(tech_data, {"name", "domain"}, f"technologies[{index}]")
        technology = Technology(
            name=_required_text(tech_data, "name", f"technologies[{index}]"),
            domain=_required_text(tech_data, "domain", f"technologies[{index}]"),
        )
        if technology.domain not in seen_domains:
            raise ConfigError(f"technologies[{index}].domain is unknown")
        technologies.append(technology)

    featured_projects: list[FeaturedProject] = []
    for index, item in enumerate(
        _list(root.get("featured_projects"), "featured_projects")
    ):
        field = f"featured_projects[{index}]"
        project_data = _mapping(item, field)
        _unknown_keys(project_data, _PROJECT_KEYS, field)
        project = FeaturedProject(
            repository=_required_text(project_data, "repository", field),
            domain=_required_text(project_data, "domain", field),
            description_en=_required_text(project_data, "description_en", field),
            description_pt=_required_text(project_data, "description_pt", field),
        )
        if project.domain not in seen_domains:
            raise ConfigError(f"{field}.domain is unknown")
        featured_projects.append(project)

    palette_data = _mapping(root.get("palette"), "palette")
    _unknown_keys(palette_data, _PALETTE_KEYS, "palette")
    colors: dict[str, str] = {}
    for key in _PALETTE_KEYS:
        color = _required_text(palette_data, key, "palette")
        if not _HEX_COLOR.fullmatch(color):
            raise ConfigError(f"palette.{key} must be #RRGGBB")
        colors[key] = color.upper()
    palette = Palette(**colors)

    return ProfileConfig(
        identity=identity,
        domains=tuple(domains),
        technologies=tuple(technologies),
        featured_projects=tuple(featured_projects),
        palette=palette,
    )
