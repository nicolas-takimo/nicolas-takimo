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
        '<text x="30" y="38" fill="#64748B" font-family="Inter,Segoe UI,sans-serif" '
        'font-size="20" font-weight="700" letter-spacing="2">MISSION TELEMETRY / TELEMETRIA</text>',
        '<line x1="30" y1="52" x2="690" y2="52" stroke="#1E293B"/>',
    ]
    for index, (key, label, value, color) in enumerate(metrics):
        column = index % 2
        row = index // 2
        cell_x = 30 + column * 345
        cell_y = 70 + row * 140
        center_x = cell_x + 157.5
        parts.extend(
            [
                f'<g data-metric="{key}">',
                f'<rect x="{cell_x}" y="{cell_y}" width="315" height="118" rx="14" '
                f'fill="{config.palette.surface}" stroke="{color}" stroke-opacity="0.24"/>',
                f'<circle cx="{cell_x + 35}" cy="{cell_y + 34}" r="11" fill="none" '
                f'stroke="{color}" stroke-opacity="0.35"/>',
                f'<circle cx="{cell_x + 35}" cy="{cell_y + 34}" r="4" fill="{color}" opacity="0.9"/>',
                f'<text x="{center_x}" y="{cell_y + 65}" fill="{config.palette.text}" '
                'font-family="Inter,Segoe UI,sans-serif" font-size="40" font-weight="700" '
                f'text-anchor="middle">{escape_text(_format_metric(value))}</text>',
                f'<text x="{center_x}" y="{cell_y + 96}" fill="{config.palette.muted}" '
                'font-family="Inter,Segoe UI,sans-serif" font-size="18" font-weight="600" '
                f'letter-spacing="1" text-anchor="middle">{escape_text(label)}</text>',
                "</g>",
            ]
        )
    return svg_document(
        width=720,
        height=360,
        title=f"Public GitHub telemetry for {config.identity.name}",
        body="".join(parts),
    )
