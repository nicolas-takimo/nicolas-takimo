import json
import subprocess
import sys
from pathlib import Path

import pytest

from generator.config import load_config
from generator.github_client import fetch_public_profile
from generator.main import publish_generated, render_all
from generator.svg import validate_svg


ROOT = Path(__file__).resolve().parents[1]
ASSET_NAMES = {
    "orbit-header.svg",
    "telemetry.svg",
    "stack-map.svg",
    "featured-projects.svg",
}


def _inputs():
    config = load_config(ROOT / "config.yml")
    payload = json.loads(
        (ROOT / "tests" / "fixtures" / "github-profile.json").read_text(
            encoding="utf-8"
        )
    )
    profile = fetch_public_profile(
        config.identity.username,
        "test-token",
        request_json=lambda _query, _variables, _token: payload,
    )
    return config, profile


def test_render_all_returns_exact_four_valid_assets():
    rendered = render_all(*_inputs())

    assert set(rendered) == ASSET_NAMES
    for svg in rendered.values():
        validate_svg(svg)


def test_fixture_cli_generates_all_assets(tmp_path):
    output = tmp_path / "generated"

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "generator.main",
            "--config",
            "config.yml",
            "--output",
            str(output),
            "--fixture",
            "tests/fixtures/github-profile.json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert {path.name for path in output.iterdir()} == ASSET_NAMES
    for asset in output.iterdir():
        validate_svg(asset.read_text(encoding="utf-8"))


def test_publish_generated_preserves_existing_assets_when_one_svg_is_invalid(
    tmp_path,
):
    output = tmp_path / "generated"
    output.mkdir()
    sentinels = {name: f"sentinel:{name}" for name in ASSET_NAMES}
    for name, content in sentinels.items():
        (output / name).write_text(content, encoding="utf-8")
    rendered = render_all(*_inputs())
    rendered["telemetry.svg"] = "<svg><broken>"

    with pytest.raises(ValueError):
        publish_generated(rendered, output)

    assert {
        name: (output / name).read_text(encoding="utf-8") for name in ASSET_NAMES
    } == sentinels


def test_publish_generated_replaces_all_assets_after_full_validation(tmp_path):
    output = tmp_path / "generated"
    output.mkdir()
    for name in ASSET_NAMES:
        (output / name).write_text(f"sentinel:{name}", encoding="utf-8")
    rendered = render_all(*_inputs())

    publish_generated(rendered, output)

    assert {
        name: (output / name).read_text(encoding="utf-8") for name in ASSET_NAMES
    } == rendered
