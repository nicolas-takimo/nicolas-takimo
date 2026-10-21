from __future__ import annotations

from collections import defaultdict

from generator.models import ProfileConfig
from generator.svg import escape_text, svg_document


_TECH_POSITIONS = {
    "Mobile": [(236, 135), (607, 137), (269, 226)],
    "Web": [(318, 118), (405, 111), (493, 116), (584, 153)],
    "IoT": [(151, 198), (335, 250), (535, 248), (680, 217)],
    "AWS": [(711, 178), (657, 258), (750, 235)],
}

_DOMAIN_POSITIONS = {
    "Mobile": (236, 157),
    "Web": (510, 154),
    "IoT": (197, 227),
    "AWS": (690, 199),
}


def _text(x: int, y: int, value: str, *, color: str, size: int, weight: int = 500) -> str:
    return (
        f'<text x="{x}" y="{y}" fill="{color}" font-family="Inter,Segoe UI,sans-serif" '
        f'font-size="{size}" font-weight="{weight}" text-anchor="middle">'
        f"{escape_text(value)}</text>"
    )


def render_orbit_header(config: ProfileConfig) -> str:
    palette = config.palette
    domain_colors = {domain.name: domain.color for domain in config.domains}
    technologies: defaultdict[str, list[str]] = defaultdict(list)
    for technology in config.technologies:
        technologies[technology.domain].append(technology.name)

    parts = [
        """
<defs>
  <radialGradient id="core" cx="50%" cy="45%" r="60%">
    <stop offset="0%" stop-color="#22D3EE" stop-opacity="0.95"/>
    <stop offset="100%" stop-color="#0E7490" stop-opacity="0.35"/>
  </radialGradient>
  <filter id="glow" x="-80%" y="-80%" width="260%" height="260%">
    <feGaussianBlur stdDeviation="5" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <pattern id="stars" width="72" height="54" patternUnits="userSpaceOnUse">
    <circle cx="8" cy="11" r="0.8" fill="#94A3B8" opacity="0.32"/>
    <circle cx="51" cy="38" r="0.6" fill="#22D3EE" opacity="0.36"/>
  </pattern>
</defs>
<rect width="850" height="300" rx="18" fill="url(#stars)"/>
""",
        _text(425, 38, config.identity.name, color=palette.text, size=24, weight=700),
        _text(425, 61, config.identity.title_en, color=palette.muted, size=12),
        _text(425, 79, config.identity.subtitle_pt, color=palette.muted, size=10),
        f'<ellipse cx="425" cy="185" rx="125" ry="35" fill="none" stroke="{palette.cyan}" stroke-opacity="0.56" transform="rotate(-8 425 185)"/>',
        f'<ellipse cx="425" cy="185" rx="170" ry="58" fill="none" stroke="{palette.violet}" stroke-opacity="0.46" transform="rotate(15 425 185)"/>',
        f'<ellipse cx="425" cy="185" rx="215" ry="77" fill="none" stroke="{palette.amber}" stroke-opacity="0.40" transform="rotate(-13 425 185)"/>',
        f'<ellipse cx="425" cy="185" rx="270" ry="98" fill="none" stroke="{palette.green}" stroke-opacity="0.33" transform="rotate(8 425 185)"/>',
        f'<circle cx="425" cy="185" r="31" fill="url(#core)" stroke="{palette.cyan}" stroke-opacity="0.85" filter="url(#glow)"/>',
        _text(425, 191, "NG", color="#ECFEFF", size=18, weight=700),
    ]

    for domain in config.domains:
        x, y = _DOMAIN_POSITIONS[domain.name]
        color = domain_colors[domain.name]
        parts.append(f'<circle cx="{x}" cy="{y - 4}" r="4" fill="{color}" filter="url(#glow)"/>')
        parts.append(_text(x, y + 14, domain.name, color=color, size=10, weight=700))

    for domain in config.domains:
        color = domain_colors[domain.name]
        positions = _TECH_POSITIONS[domain.name]
        for index, technology in enumerate(technologies[domain.name]):
            x, y = positions[index % len(positions)]
            if index >= len(positions):
                y = min(270, y + 14 * (index // len(positions)))
            parts.append(f'<circle cx="{x}" cy="{y - 3}" r="2.5" fill="{color}"/>')
            parts.append(_text(x, y + 10, technology, color=color, size=9))

    parts.append(
        _text(
            425,
            286,
            "MOBILE · WEB · IoT · AWS",
            color=palette.muted,
            size=9,
            weight=600,
        )
    )
    return svg_document(
        width=850,
        height=300,
        title=f"Technology orbit for {config.identity.name}",
        body="".join(parts),
    )
