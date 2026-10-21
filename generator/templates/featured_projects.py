from __future__ import annotations

from textwrap import wrap

from generator.models import ProfileConfig, PublicProfileData
from generator.svg import escape_text, svg_document


def _lines(text: str, width: int, limit: int) -> list[str]:
    chunks = wrap(text, width=width, break_long_words=False, break_on_hyphens=False)
    if len(chunks) <= limit:
        return chunks
    visible = chunks[:limit]
    visible[-1] = visible[-1].rstrip(". ") + "…"
    return visible


def _title_lines(text: str) -> list[str]:
    chunks = wrap(text, width=31, break_long_words=True, break_on_hyphens=True)
    if len(chunks) <= 2:
        return chunks
    return [chunks[0], chunks[1].rstrip("- ") + "…"]


def render_featured_projects(
    config: ProfileConfig,
    profile: PublicProfileData,
) -> str:
    palette = config.palette
    colors = {domain.name: domain.color for domain in config.domains}
    parts = [
        '<text x="38" y="34" fill="#64748B" font-family="Inter,Segoe UI,sans-serif" '
        'font-size="10" font-weight="700" letter-spacing="3">FEATURED SYSTEMS / PROJETOS</text>',
        '<line x1="38" y1="48" x2="812" y2="48" stroke="#1E293B"/>',
    ]

    for index, project in enumerate(config.featured_projects):
        x = 35 + index * 270
        y = 67
        color = colors[project.domain]
        remote = profile.repositories.get(project.repository)
        remote_attribute = (
            f' data-repository-url="{escape_text(remote.url)}"' if remote else ""
        )
        parts.extend(
            [
                f'<g data-repository="{escape_text(project.repository)}"{remote_attribute} '
                f'data-description-en="{escape_text(project.description_en)}" '
                f'data-description-pt="{escape_text(project.description_pt)}">',
                f'<desc>{escape_text(project.description_en)} {escape_text(project.description_pt)}</desc>',
                f'<rect x="{x}" y="{y}" width="240" height="206" rx="14" '
                f'fill="{palette.surface}" stroke="{color}" stroke-opacity="0.25"/>',
                f'<circle cx="{x + 120}" cy="{y + 30}" r="12" fill="none" '
                f'stroke="{color}" stroke-opacity="0.32"/>',
                f'<circle cx="{x + 120}" cy="{y + 30}" r="4" fill="{color}"/>',
            ]
        )
        title_lines = _title_lines(project.repository)
        for line_index, line in enumerate(title_lines):
            parts.append(
                f'<text data-kind="repository-title" x="{x + 120}" y="{y + 59 + line_index * 13}" '
                f'fill="{palette.text}" font-family="Inter,Segoe UI,sans-serif" font-size="10" '
                f'font-weight="700" text-anchor="middle">{escape_text(line)}</text>'
            )

        en_y = y + 91
        for line_index, line in enumerate(_lines(project.description_en, 39, 2)):
            parts.append(
                f'<text x="{x + 16}" y="{en_y + line_index * 13}" fill="{palette.text}" '
                f'font-family="Inter,Segoe UI,sans-serif" font-size="8.5">{escape_text(line)}</text>'
            )
        pt_y = y + 130
        for line_index, line in enumerate(_lines(project.description_pt, 39, 3)):
            parts.append(
                f'<text x="{x + 16}" y="{pt_y + line_index * 13}" fill="{palette.muted}" '
                f'font-family="Inter,Segoe UI,sans-serif" font-size="8.5">{escape_text(line)}</text>'
            )
        parts.extend(
            [
                f'<rect x="{x + 73}" y="{y + 178}" width="94" height="18" rx="9" '
                f'fill="{color}" opacity="0.14"/>',
                f'<text x="{x + 120}" y="{y + 191}" fill="{color}" '
                'font-family="Inter,Segoe UI,sans-serif" font-size="8.5" font-weight="700" '
                f'text-anchor="middle">{escape_text(project.domain)}</text>',
                "</g>",
            ]
        )

    return svg_document(
        width=850,
        height=300,
        title=f"Featured projects by {config.identity.name}",
        body="".join(parts),
    )
