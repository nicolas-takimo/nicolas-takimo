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
        '<text x="30" y="38" fill="#64748B" font-family="Inter,Segoe UI,sans-serif" '
        'font-size="20" font-weight="700" letter-spacing="2">FEATURED SYSTEMS / PROJETOS</text>',
        '<line x1="30" y1="52" x2="690" y2="52" stroke="#1E293B"/>',
    ]

    for index, project in enumerate(config.featured_projects):
        x = 36
        y = 70 + index * 290
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
                f'<rect x="{x}" y="{y}" width="648" height="260" rx="16" '
                f'fill="{palette.surface}" stroke="{color}" stroke-opacity="0.25"/>',
                f'<circle cx="{x + 35}" cy="{y + 35}" r="14" fill="none" '
                f'stroke="{color}" stroke-opacity="0.32"/>',
                f'<circle cx="{x + 35}" cy="{y + 35}" r="5" fill="{color}"/>',
            ]
        )
        title_lines = _title_lines(project.repository)
        for line_index, line in enumerate(title_lines):
            parts.append(
                f'<text data-kind="repository-title" x="{x + 324}" y="{y + 43 + line_index * 27}" '
                f'fill="{palette.text}" font-family="Inter,Segoe UI,sans-serif" font-size="22" '
                f'font-weight="700" text-anchor="middle">{escape_text(line)}</text>'
            )

        en_y = y + 112
        for line_index, line in enumerate(_lines(project.description_en, 68, 2)):
            parts.append(
                f'<text x="{x + 24}" y="{en_y + line_index * 24}" fill="{palette.text}" '
                f'font-family="Inter,Segoe UI,sans-serif" font-size="18">{escape_text(line)}</text>'
            )
        pt_y = y + 172
        for line_index, line in enumerate(_lines(project.description_pt, 68, 2)):
            parts.append(
                f'<text x="{x + 24}" y="{pt_y + line_index * 24}" fill="{palette.muted}" '
                f'font-family="Inter,Segoe UI,sans-serif" font-size="18">{escape_text(line)}</text>'
            )
        parts.extend(
            [
                f'<rect x="{x + 230}" y="{y + 222}" width="188" height="26" rx="13" '
                f'fill="{color}" opacity="0.14"/>',
                f'<text x="{x + 324}" y="{y + 242}" fill="{color}" '
                'font-family="Inter,Segoe UI,sans-serif" font-size="18" font-weight="700" '
                f'text-anchor="middle">{escape_text(project.domain)}</text>',
                "</g>",
            ]
        )

    return svg_document(
        width=720,
        height=950,
        title=f"Featured projects by {config.identity.name}",
        body="".join(parts),
    )
