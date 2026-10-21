from dataclasses import replace
from pathlib import Path
from xml.etree import ElementTree

from generator.config import load_config
from generator.svg import escape_text, svg_document, validate_svg
from generator.templates.orbit_header import render_orbit_header


ROOT = Path(__file__).resolve().parents[1]


def _config():
    return load_config(ROOT / "config.yml")


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
