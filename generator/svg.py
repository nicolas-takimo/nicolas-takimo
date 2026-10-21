from __future__ import annotations

from html import escape
from xml.etree import ElementTree


def escape_text(value: str) -> str:
    return escape(value, quote=True)


def svg_document(*, width: int, height: int, title: str, body: str) -> str:
    safe_title = escape_text(title)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        'role="img" aria-labelledby="svg-title">'
        f'<title id="svg-title">{safe_title}</title>'
        f'<rect width="{width}" height="{height}" rx="18" fill="#050914"/>'
        f"{body}"
        "</svg>"
    )


def validate_svg(svg: str) -> None:
    try:
        root = ElementTree.fromstring(svg)
    except ElementTree.ParseError as exc:
        raise ValueError(f"generated SVG is not valid XML: {exc}") from exc
    if root.tag != "{http://www.w3.org/2000/svg}svg":
        raise ValueError("generated document is not an SVG root")
    if root.attrib.get("role") != "img":
        raise ValueError("generated SVG must declare role=img")
    title = root.find("{http://www.w3.org/2000/svg}title")
    if title is None or not (title.text or "").strip():
        raise ValueError("generated SVG must include a non-empty title")
