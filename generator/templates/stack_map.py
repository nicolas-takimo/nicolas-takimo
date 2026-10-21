from __future__ import annotations

from collections import defaultdict

from generator.models import ProfileConfig, PublicProfileData
from generator.svg import escape_text, svg_document


def render_stack_map(config: ProfileConfig, profile: PublicProfileData) -> str:
    palette = config.palette
    parts = [
        '<text x="38" y="34" fill="#64748B" font-family="Inter,Segoe UI,sans-serif" '
        'font-size="10" font-weight="700" letter-spacing="3">STACK SIGNALS / MAPA DE STACK</text>',
        '<line x1="38" y1="48" x2="812" y2="48" stroke="#1E293B"/>',
        f'<text x="42" y="70" fill="{palette.muted}" font-family="Inter,Segoe UI,sans-serif" '
        'font-size="9" font-weight="700" letter-spacing="1.5">PUBLIC LANGUAGE TELEMETRY</text>',
        f'<text x="468" y="70" fill="{palette.muted}" font-family="Inter,Segoe UI,sans-serif" '
        'font-size="9" font-weight="700" letter-spacing="1.5">ENGINEERING DOMAINS</text>',
        '<line x1="438" y1="66" x2="438" y2="300" stroke="#1E293B"/>',
    ]

    all_language_bytes = profile.language_bytes or {}
    languages = sorted(
        all_language_bytes.items(), key=lambda item: (-item[1], item[0])
    )[:7]
    if languages:
        total = sum(max(0, value) for value in all_language_bytes.values()) or 1
        maximum = max(size for _, size in languages) or 1
        for index, (language, size) in enumerate(languages):
            y = 90 + index * 31
            width = max(4.0, min(360.0, 360.0 * size / maximum))
            percentage = size / total * 100
            parts.extend(
                [
                    f'<text x="42" y="{y}" fill="{palette.text}" font-family="Inter,Segoe UI,sans-serif" '
                    f'font-size="10">{escape_text(language)}</text>',
                    f'<text x="408" y="{y}" fill="{palette.muted}" font-family="Inter,Segoe UI,sans-serif" '
                    f'font-size="9" text-anchor="end">{percentage:.1f}%</text>',
                    f'<rect x="42" y="{y + 7}" width="360" height="7" rx="3.5" fill="#172033"/>',
                    f'<rect data-language="{escape_text(language)}" x="42" y="{y + 7}" '
                    f'width="{width:.2f}" height="7" rx="3.5" fill="{palette.cyan}" opacity="0.82"/>',
                ]
            )
    else:
        parts.append(
            f'<text x="42" y="110" fill="{palette.muted}" font-family="Inter,Segoe UI,sans-serif" '
            'font-size="11">No public language data / sem dados públicos</text>'
        )

    technology_by_domain: defaultdict[str, list[str]] = defaultdict(list)
    for technology in config.technologies:
        technology_by_domain[technology.domain].append(technology.name)

    positions = ((468, 86), (648, 86), (468, 202), (648, 202))
    for domain, (x, y) in zip(config.domains, positions, strict=True):
        parts.extend(
            [
                f'<rect x="{x}" y="{y}" width="164" height="99" rx="12" '
                f'fill="{palette.surface}" stroke="{domain.color}" stroke-opacity="0.24"/>',
                f'<circle cx="{x + 17}" cy="{y + 20}" r="5" fill="{domain.color}"/>',
                f'<text data-kind="domain" x="{x + 31}" y="{y + 24}" fill="{domain.color}" '
                'font-family="Inter,Segoe UI,sans-serif" font-size="12" font-weight="700">'
                f'{escape_text(domain.name)}</text>',
            ]
        )
        for index, technology in enumerate(technology_by_domain[domain.name]):
            column = index % 2
            row = index // 2
            text_x = x + 14 + column * 77
            text_y = y + 53 + row * 24
            parts.extend(
                [
                f'<circle cx="{text_x}" cy="{text_y - 3}" r="1.8" fill="{domain.color}"/>',
                f'<text data-kind="technology" x="{text_x + 7}" y="{text_y}" '
                f'fill="{palette.text}" font-family="Inter,Segoe UI,sans-serif" font-size="9">'
                f'{escape_text(technology)}</text>',
                ]
            )

    return svg_document(
        width=850,
        height=330,
        title=f"Technology stack map for {config.identity.name}",
        body="".join(parts),
    )
