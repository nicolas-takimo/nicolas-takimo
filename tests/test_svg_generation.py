import json
from dataclasses import replace
from pathlib import Path
from xml.etree import ElementTree

import pytest

from generator.config import load_config
from generator.github_client import fetch_public_profile
from generator.svg import escape_text, svg_document, validate_svg
from generator.templates.orbit_header import render_orbit_header
from generator.templates.stack_map import render_stack_map
from generator.templates.telemetry import render_telemetry


ROOT = Path(__file__).resolve().parents[1]


def _config():
    return load_config(ROOT / "config.yml")


def _profile(fixture="github-profile.json"):
    payload = json.loads(
        (ROOT / "tests" / "fixtures" / fixture).read_text(encoding="utf-8")
    )
    return fetch_public_profile(
        "nicolas-takimo",
        "test-token",
        request_json=lambda _query, _variables, _token: payload,
    )


def test_orbit_header_is_valid_accessible_svg():
    config = _config()

    svg = render_orbit_header(config)
    validate_svg(svg)
    root = ElementTree.fromstring(svg)

    assert root.attrib["viewBox"] == "0 0 850 300"
    assert root.attrib["role"] == "img"
    assert root.find("{http://www.w3.org/2000/svg}title") is not None
    assert "Nicolas Gabriel" in svg
    for domain in ("Mobile", "Web", "IoT", "AWS"):
        assert domain in svg
    for technology in config.technologies:
        assert technology.name in svg


def test_orbit_header_escapes_xml_sensitive_text():
    config = _config()
    unsafe_identity = replace(config.identity, name="Nicolas & Gabriel <Dev>")

    svg = render_orbit_header(replace(config, identity=unsafe_identity))

    ElementTree.fromstring(svg)
    assert "Nicolas &amp; Gabriel &lt;Dev&gt;" in svg


def test_escape_text_handles_xml_sensitive_characters():
    assert escape_text('A&B <C> "D"') == "A&amp;B &lt;C&gt; &quot;D&quot;"


def test_svg_document_sets_accessible_root_and_title():
    svg = svg_document(width=850, height=100, title="A & B", body="<g />")

    validate_svg(svg)
    root = ElementTree.fromstring(svg)
    assert root.tag == "{http://www.w3.org/2000/svg}svg"
    assert root.attrib["viewBox"] == "0 0 850 100"
    assert root.attrib["role"] == "img"
    assert root.attrib["aria-labelledby"] == "svg-title"
    assert "<title id=\"svg-title\">A &amp; B</title>" in svg


def test_telemetry_renders_four_verified_public_metrics():
    svg = render_telemetry(_config(), _profile())

    validate_svg(svg)
    assert "MISSION TELEMETRY / TELEMETRIA" in svg
    for label in ("PUBLIC REPOS", "CONTRIBUTIONS", "FOLLOWERS", "LANGUAGES"):
        assert label in svg
    for metric, value in {
        "repositories": "2",
        "contributions": "58",
        "followers": "14",
        "languages": "3",
    }.items():
        root = ElementTree.fromstring(svg)
        group = root.find(f".//*[@data-metric='{metric}']")
        assert group is not None
        assert value in "".join(group.itertext())


def test_telemetry_uses_em_dash_for_none():
    svg = render_telemetry(_config(), _profile("github-profile-partial.json"))
    root = ElementTree.fromstring(svg)

    for metric in ("contributions", "followers"):
        group = root.find(f".//*[@data-metric='{metric}']")
        assert group is not None
        metric_text = "".join(group.itertext())
        assert "—" in metric_text
        assert "0" not in metric_text


def test_stack_map_contains_all_declared_domains_and_technologies():
    config = _config()
    svg = render_stack_map(config, _profile())
    root = ElementTree.fromstring(svg)

    validate_svg(svg)
    domain_labels = [
        "".join(node.itertext())
        for node in root.findall(".//*[@data-kind='domain']")
    ]
    technology_labels = [
        "".join(node.itertext())
        for node in root.findall(".//*[@data-kind='technology']")
    ]
    assert domain_labels == [domain.name for domain in config.domains]
    assert technology_labels == [technology.name for technology in config.technologies]


def test_stack_map_uses_public_language_bytes_for_bar_proportions():
    root = ElementTree.fromstring(render_stack_map(_config(), _profile()))
    bars = {
        node.attrib["data-language"]: float(node.attrib["width"])
        for node in root.findall(".//*[@data-language]")
    }

    assert bars["TypeScript"] == 360
    assert bars["Python"] > bars["CSS"] >= 4
    assert bars["Python"] / bars["TypeScript"] == pytest.approx(400 / 740, rel=0.01)
    assert all(4 <= width <= 360 for width in bars.values())


def test_stack_map_keeps_declared_technologies_when_language_data_is_empty():
    config = _config()
    empty_profile = replace(_profile(), language_count=0, language_bytes={})
    root = ElementTree.fromstring(render_stack_map(config, empty_profile))

    technology_labels = [
        "".join(node.itertext())
        for node in root.findall(".//*[@data-kind='technology']")
    ]
    assert technology_labels == [technology.name for technology in config.technologies]
    assert root.findall(".//*[@data-language]") == []
