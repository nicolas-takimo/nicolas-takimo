from __future__ import annotations

from generator.models import ProfileConfig, PublicProfileData
from generator.svg import escape_text, svg_document


def _format_metric(value: int | None) -> str:
    if value is None:
        return "—"
    if value >= 1000:
        return f"{value / 1000:.1f}k"
    return str(value)


def render_telemetry(config: ProfileConfig, profile: PublicProfileData) -> str:
    metrics = (
        ("repositories", "PUBLIC REPOS", profile.public_repository_count, config.palette.cyan),
        ("contributions", "CONTRIBUTIONS", profile.contributions_year, config.palette.amber),
        ("followers", "FOLLOWERS", profile.followers, config.palette.violet),
        ("languages", "LANGUAGES", profile.language_count, config.palette.green),
    )
    parts = [
        '<text x="38" y="34" fill="#64748B" font-family="Inter,Segoe UI,sans-serif" '
        'font-size="10" font-weight="700" letter-spacing="3">MISSION TELEMETRY / TELEMETRIA</text>',
        '<line x1="38" y1="48" x2="812" y2="48" stroke="#1E293B"/>',
    ]
    for index, (key, label, value, color) in enumerate(metrics):
        cell_x = 35 + index * 198
        center_x = cell_x + 99
        if index:
            parts.append(
                f'<line x1="{cell_x}" y1="67" x2="{cell_x}" y2="153" '
                'stroke="#1E293B"/>'
            )
        parts.extend(
            [
                f'<g data-metric="{key}">',
                f'<circle cx="{center_x}" cy="87" r="13" fill="none" stroke="{color}" stroke-opacity="0.28"/>',
                f'<circle cx="{center_x}" cy="87" r="5" fill="{color}" opacity="0.86"/>',
                f'<text x="{center_x}" y="126" fill="{config.palette.text}" '
                'font-family="Inter,Segoe UI,sans-serif" font-size="26" font-weight="700" '
                f'text-anchor="middle">{escape_text(_format_metric(value))}</text>',
                f'<text x="{center_x}" y="147" fill="{config.palette.muted}" '
                'font-family="Inter,Segoe UI,sans-serif" font-size="9" font-weight="600" '
                f'letter-spacing="1.2" text-anchor="middle">{escape_text(label)}</text>',
                "</g>",
            ]
        )
    return svg_document(
        width=850,
        height=180,
        title=f"Public GitHub telemetry for {config.identity.name}",
        body="".join(parts),
    )
