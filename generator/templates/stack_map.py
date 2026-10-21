from __future__ import annotations

from collections import defaultdict

from generator.models import ProfileConfig, PublicProfileData
from generator.svg import escape_text, svg_document


def render_stack_map(config: ProfileConfig, profile: PublicProfileData) -> str:
    palette = config.palette
    parts = [
        '<text x="30" y="38" fill="#64748B" font-family="Inter,Segoe UI,sans-serif" '
        'font-size="20" font-weight="700" letter-spacing="2">STACK SIGNALS / MAPA DE STACK</text>',
        '<line x1="30" y1="52" x2="690" y2="52" stroke="#1E293B"/>',
        f'<text x="36" y="82" fill="{palette.muted}" font-family="Inter,Segoe UI,sans-serif" '
        'font-size="18" font-weight="700" letter-spacing="1">PUBLIC LANGUAGE TELEMETRY</text>',
    ]

    all_language_bytes = profile.language_bytes or {}
    languages = sorted(
        all_language_bytes.items(), key=lambda item: (-item[1], item[0])
    )[:7]
    if languages:
        total = sum(max(0, value) for value in all_language_bytes.values()) or 1
        maximum = max(size for _, size in languages) or 1
        for index, (language, size) in enumerate(languages):
            y = 115 + index * 45
            width = max(4.0, min(360.0, 360.0 * size / maximum))
            percentage = size / total * 100
            parts.extend(
                [
                    f'<text x="36" y="{y}" fill="{palette.text}" font-family="Inter,Segoe UI,sans-serif" '
                    f'font-size="18">{escape_text(language)}</text>',
                    f'<text x="420" y="{y}" fill="{palette.muted}" font-family="Inter,Segoe UI,sans-serif" '
                    f'font-size="18" text-anchor="end">{percentage:.1f}%</text>',
                    f'<rect x="36" y="{y + 10}" width="360" height="10" rx="5" fill="#172033"/>',
                    f'<rect data-language="{escape_text(language)}" x="36" y="{y + 10}" '
                    f'width="{width:.2f}" height="10" rx="5" fill="{palette.cyan}" opacity="0.82"/>',
                ]
            )
    else:
        parts.append(
            f'<text x="36" y="125" fill="{palette.muted}" font-family="Inter,Segoe UI,sans-serif" '
            'font-size="18">No public language data / sem dados públicos</text>'
        )

    parts.extend(
        [
            '<line x1="30" y1="440" x2="690" y2="440" stroke="#1E293B"/>',
            f'<text x="36" y="474" fill="{palette.muted}" font-family="Inter,Segoe UI,sans-serif" '
            'font-size="18" font-weight="700" letter-spacing="1">ENGINEERING DOMAINS</text>',
        ]
    )

    technology_by_domain: defaultdict[str, list[str]] = defaultdict(list)
    for technology in config.technologies:
        technology_by_domain[technology.domain].append(technology.name)

    positions = ((36, 495), (369, 495), (36, 680), (369, 680))
    for domain, (x, y) in zip(config.domains, positions, strict=True):
        parts.extend(
            [
                f'<rect x="{x}" y="{y}" width="315" height="165" rx="14" '
                f'fill="{palette.surface}" stroke="{domain.color}" stroke-opacity="0.24"/>',
                f'<circle cx="{x + 24}" cy="{y + 30}" r="7" fill="{domain.color}"/>',
                f'<text data-kind="domain" x="{x + 44}" y="{y + 37}" fill="{domain.color}" '
                'font-family="Inter,Segoe UI,sans-serif" font-size="22" font-weight="700">'
                f'{escape_text(domain.name)}</text>',
            ]
        )
        for index, technology in enumerate(technology_by_domain[domain.name]):
            column = index % 2
            row = index // 2
            text_x = x + 20 + column * 150
            text_y = y + 82 + row * 42
            parts.extend(
                [
                f'<circle cx="{text_x}" cy="{text_y - 5}" r="3" fill="{domain.color}"/>',
                f'<text data-kind="technology" x="{text_x + 10}" y="{text_y}" '
                f'fill="{palette.text}" font-family="Inter,Segoe UI,sans-serif" font-size="18">'
                f'{escape_text(technology)}</text>',
                ]
            )

    return svg_document(
        width=720,
        height=860,
        title=f"Technology stack map for {config.identity.name}",
        body="".join(parts),
    )
