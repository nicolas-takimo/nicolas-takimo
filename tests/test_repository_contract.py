import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
WORKFLOW = ROOT / ".github" / "workflows" / "generate-profile.yml"
ASSETS = {
    "assets/generated/orbit-header.svg",
    "assets/generated/telemetry.svg",
    "assets/generated/stack-map.svg",
    "assets/generated/featured-projects.svg",
}
PROJECT_URLS = {
    "https://github.com/nicolas-takimo/gavioes-style-fluxos",
    "https://github.com/nicolas-takimo/graze",
    "https://github.com/nicolas-takimo/TCC-Controle-de-acesso-remoto-usando-Digiprox-S--202",
}


def _readme():
    return README.read_text(encoding="utf-8")


def _workflow():
    return yaml.load(WORKFLOW.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)


def test_readme_identifies_nicolas_bilingually():
    readme = _readme()

    assert "Nicolas Gabriel" in readme
    assert "Computer Engineer · Full-Stack Developer" in readme
    assert "Engenheiro da Computação criando produtos conectados de ponta a ponta" in readme
    assert "Mobile · Web · IoT · AWS" in readme
    assert "CTO @ FireTheBox" in readme


def test_readme_references_exact_four_local_assets():
    readme = _readme()
    referenced_assets = {
        source.removeprefix("./")
        for source in re.findall(r'<img\s+src="([^"]+\.svg)"', readme)
    }

    assert referenced_assets == ASSETS
    assert all((ROOT / path).is_file() for path in ASSETS)
    assert readme.count('width="850"') == 4
    assert readme.count('alt="') >= 4


def test_readme_links_exact_three_featured_repositories():
    readme = _readme()
    project_urls = {
        url
        for url in re.findall(r"https://github\.com/nicolas-takimo/[^)\s]+", readme)
        if url != "https://github.com/nicolas-takimo"
    }

    assert project_urls == PROJECT_URLS


def test_readme_contains_no_unconfirmed_contact_links():
    readme = _readme().lower()

    assert "mailto:" not in readme
    assert "linkedin.com" not in readme
    assert "portfolio" not in readme
    assert "visitor" not in readme
    assert "github-readme-stats" not in readme


def test_workflow_has_daily_manual_and_scoped_push_triggers():
    workflow = _workflow()
    triggers = workflow["on"]

    assert set(triggers) == {"workflow_dispatch", "schedule", "push"}
    assert triggers["schedule"] == [{"cron": "17 8 * * *"}]
    push_paths = set(triggers["push"]["paths"])
    assert {
        "generator/**",
        "config.yml",
        "tests/**",
        ".github/workflows/generate-profile.yml",
        "requirements.txt",
        "requirements-dev.txt",
    } <= push_paths
    assert "assets/generated/**" not in push_paths


def test_workflow_uses_python_312_and_github_token():
    workflow = _workflow()
    steps = workflow["jobs"]["generate"]["steps"]
    setup = next(step for step in steps if step.get("uses", "").startswith("actions/setup-python@"))
    generate = next(step for step in steps if step.get("name") == "Generate live profile assets")

    assert setup["with"]["python-version"] == "3.12"
    assert generate["env"]["GITHUB_TOKEN"] == "${{ secrets.GITHUB_TOKEN }}"
    assert generate["run"] == "python -m generator.main"


def test_workflow_grants_only_contents_write():
    workflow = _workflow()

    assert workflow["permissions"] == {"contents": "write"}


def test_workflow_commits_only_when_git_diff_is_nonempty():
    workflow = _workflow()
    steps = workflow["jobs"]["generate"]["steps"]
    detect = next(step for step in steps if step.get("id") == "changes")
    commit = next(step for step in steps if step.get("name") == "Commit generated assets")

    assert "git diff --quiet -- assets/generated" in detect["run"]
    assert commit["if"] == "steps.changes.outputs.changed == 'true'"
    assert "assets/generated/*.svg" in commit["run"]
    assert "[skip ci]" in commit["run"]
