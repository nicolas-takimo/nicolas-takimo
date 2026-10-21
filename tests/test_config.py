from pathlib import Path

import pytest
import yaml

from generator.config import ConfigError, load_config


ROOT = Path(__file__).resolve().parents[1]


def test_load_config_returns_validated_profile_config():
    config = load_config(ROOT / "config.yml")

    assert config.identity.username == "nicolas-takimo"
    assert [domain.name for domain in config.domains] == [
        "Mobile",
        "Web",
        "IoT",
        "AWS",
    ]
    technology_names = {technology.name for technology in config.technologies}
    assert {"React Native", "Flutter"} <= technology_names
    assert [project.repository for project in config.featured_projects] == [
        "gavioes-style-fluxos",
        "graze",
        "TCC-Controle-de-acesso-remoto-usando-Digiprox-S--202",
    ]
    assert config.identity.email is None
    assert config.identity.linkedin_url is None
    assert config.identity.portfolio_url is None


def _valid_config():
    return {
        "identity": {
            "username": "nicolas-takimo",
            "name": "Nicolas Gabriel",
            "title_en": "Computer Engineer · Full-Stack Developer",
            "subtitle_pt": "Engenheiro da Computação",
            "company": "FireTheBox",
            "location": "Mato Grosso, Brasil",
            "email": None,
            "linkedin_url": None,
            "portfolio_url": None,
        },
        "domains": [
            {"name": "Mobile", "color": "#A855F7"},
            {"name": "Web", "color": "#22D3EE"},
            {"name": "IoT", "color": "#F59E0B"},
            {"name": "AWS", "color": "#22C55E"},
        ],
        "technologies": [
            {"name": "Flutter", "domain": "Mobile"},
        ],
        "featured_projects": [
            {
                "repository": "project",
                "domain": "Web",
                "description_en": "English description",
                "description_pt": "Descrição em português",
            }
        ],
        "palette": {
            "background": "#050914",
            "surface": "#0F172A",
            "text": "#E2E8F0",
            "muted": "#94A3B8",
            "cyan": "#22D3EE",
            "violet": "#A855F7",
            "green": "#22C55E",
            "amber": "#F59E0B",
        },
    }


def _write_config(tmp_path, data):
    config_path = tmp_path / "config.yml"
    config_path.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    return config_path


def test_load_config_rejects_missing_identity(tmp_path):
    data = _valid_config()
    del data["identity"]

    with pytest.raises(ConfigError, match="identity"):
        load_config(_write_config(tmp_path, data))


def test_load_config_rejects_duplicate_domain(tmp_path):
    data = _valid_config()
    data["domains"].append({"name": "Mobile", "color": "#FFFFFF"})

    with pytest.raises(ConfigError, match="domains"):
        load_config(_write_config(tmp_path, data))


def test_load_config_rejects_unknown_featured_repository_shape(tmp_path):
    data = _valid_config()
    data["featured_projects"][0]["unknown"] = "not allowed"

    with pytest.raises(ConfigError, match=r"featured_projects\[0\]\.unknown"):
        load_config(_write_config(tmp_path, data))


def test_load_config_rejects_non_hex_palette_color(tmp_path):
    data = _valid_config()
    data["palette"]["background"] = "navy"

    with pytest.raises(ConfigError, match="palette.background"):
        load_config(_write_config(tmp_path, data))
