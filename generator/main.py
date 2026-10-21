from __future__ import annotations

import argparse
import json
import os
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path

from generator.config import load_config
from generator.github_client import fetch_public_profile
from generator.models import ProfileConfig, PublicProfileData
from generator.svg import validate_svg
from generator.templates.featured_projects import render_featured_projects
from generator.templates.orbit_header import render_orbit_header
from generator.templates.stack_map import render_stack_map
from generator.templates.telemetry import render_telemetry


ASSET_NAMES = (
    "orbit-header.svg",
    "telemetry.svg",
    "stack-map.svg",
    "featured-projects.svg",
)


def render_all(
    config: ProfileConfig,
    profile: PublicProfileData,
) -> dict[str, str]:
    return {
        "orbit-header.svg": render_orbit_header(config),
        "telemetry.svg": render_telemetry(config, profile),
        "stack-map.svg": render_stack_map(config, profile),
        "featured-projects.svg": render_featured_projects(config, profile),
    }


def publish_generated(rendered: Mapping[str, str], output_dir: Path) -> None:
    if set(rendered) != set(ASSET_NAMES):
        raise ValueError(f"expected exactly these assets: {', '.join(ASSET_NAMES)}")
    for svg in rendered.values():
        validate_svg(svg)

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=f".{output_dir.name}-",
        dir=output_dir.parent,
    ) as staging_name:
        staging_dir = Path(staging_name)
        for name in ASSET_NAMES:
            staged = staging_dir / name
            with staged.open("w", encoding="utf-8", newline="\n") as handle:
                handle.write(rendered[name])
                handle.flush()
                os.fsync(handle.fileno())
        output_dir.mkdir(parents=True, exist_ok=True)
        for name in ASSET_NAMES:
            os.replace(staging_dir / name, output_dir / name)


def _load_fixture_profile(
    config: ProfileConfig,
    fixture_path: Path,
) -> PublicProfileData:
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    return fetch_public_profile(
        config.identity.username,
        "fixture-token",
        request_json=lambda _query, _variables, _token: payload,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate GitHub profile SVG assets")
    parser.add_argument("--config", type=Path, default=Path("config.yml"))
    parser.add_argument("--output", type=Path, default=Path("assets/generated"))
    parser.add_argument("--fixture", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    config = load_config(args.config)
    if args.fixture:
        profile = _load_fixture_profile(config, args.fixture)
    else:
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            raise SystemExit("GITHUB_TOKEN is required when --fixture is not used")
        profile = fetch_public_profile(config.identity.username, token)
    rendered = render_all(config, profile)
    publish_generated(rendered, args.output)
    print(f"Generated {len(rendered)} profile assets in {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
