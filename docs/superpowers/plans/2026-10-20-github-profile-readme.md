# GitHub Profile README Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and publish the public `nicolas-takimo/nicolas-takimo` profile repository with a bilingual README and four automatically refreshed, original SVG panels.

**Architecture:** A small Python generator loads curated content from `config.yml`, fetches public GitHub data through one GraphQL client, normalizes it into typed dataclasses, and renders four independent SVG templates. An orchestrator validates every SVG in a temporary directory before replacing the published assets; GitHub Actions runs tests, regenerates daily or on demand, and commits only real changes.

**Tech Stack:** Python 3.12, Python standard library, PyYAML 6.x, pytest 8.x, CairoSVG 2.7.x for render checks, GitHub GraphQL API, GitHub Actions, Markdown, SVG.

**Spec:** `docs/superpowers/specs/2026-10-20-github-profile-readme-design.md`

## Global Constraints

- Repository and GitHub profile target: public `nicolas-takimo/nicolas-takimo` on branch `main`.
- Copy is bilingual: technical headings in English with concise Portuguese context.
- Professional identity is `Nicolas Gabriel`, `Computer Engineer · Full-Stack Developer`, `CTO @ FireTheBox`, `Mato Grosso, Brasil`.
- Focus domains are exactly Mobile, Web, IoT, and AWS.
- Declared stack includes TypeScript, React, Next.js, Node.js, Python, React Native, Flutter, Firebase, RFID, AWS, and GitHub Actions.
- Never expose private repositories, private contributions, secrets, unconfirmed contact links, invented experience, clients, or metrics.
- Generated assets are `assets/generated/orbit-header.svg`, `telemetry.svg`, `stack-map.svg`, and `featured-projects.svg`.
- Published SVGs use a common `viewBox="0 0 850 …"`, high-contrast labels, explicit text labels in addition to color, and valid XML.
- Remote failures must leave the last valid generated assets untouched.
- Workflow permission is limited to `contents: write`; authentication uses only the repository-provided `GITHUB_TOKEN`.

## Review Focus

- XML-sensitive characters in names, descriptions, or repositories must be escaped and still produce parseable SVG; pinned by Task 3.
- Null or absent GitHub fields must become explicit unavailable values (`None` in models and `—` in visuals), never guessed zeroes; pinned by Tasks 2 and 4.
- Forks and private repositories must not affect public repository, project, or language metrics; pinned by Task 2.
- API/rate-limit failure or one invalid template must preserve all previously published assets; pinned by Task 5.
- An unchanged regeneration must not create a commit or workflow loop; pinned by Task 6.

---

## File Structure

- `config.yml`: curated bilingual identity, stack, palette, and featured-project metadata.
- `requirements.txt`: runtime dependency on PyYAML.
- `requirements-dev.txt`: pytest and CairoSVG test dependencies.
- `generator/models.py`: immutable normalized configuration and GitHub data models.
- `generator/config.py`: parse and validate `config.yml` into models.
- `generator/github_client.py`: GraphQL transport, response validation, and public-data normalization.
- `generator/svg.py`: shared XML escaping, text, panel, and document helpers plus XML validation.
- `generator/templates/*.py`: one module per visual panel; no network or file I/O.
- `generator/main.py`: CLI, fixture mode, render orchestration, and staged publication.
- `tests/fixtures/*.json`: deterministic GitHub success, partial-data, and failure fixtures.
- `tests/test_*.py`: unit and integration coverage.
- `README.md`: profile copy and links to the four local generated assets.
- `.github/workflows/generate-profile.yml`: test, generate, and conditional-commit automation.

### Task 1: Configuration and typed domain models

**Files:**
- Create: `config.yml`
- Create: `requirements.txt`
- Create: `requirements-dev.txt`
- Create: `generator/__init__.py`
- Create: `generator/models.py`
- Create: `generator/config.py`
- Create: `tests/test_config.py`

**Interfaces:**
- Consumes: no earlier task interfaces.
- Produces: immutable dataclasses `Identity`, `Technology`, `FeaturedProject`, `Palette`, and `ProfileConfig`; `load_config(path: Path) -> ProfileConfig`; `ConfigError(ValueError)`.

- [ ] **Step 1: Write the failing happy-path configuration test**

Create `test_load_config_returns_validated_profile_config` asserting the repository config yields username `nicolas-takimo`, four domains in the order `Mobile, Web, IoT, AWS`, both `React Native` and `Flutter`, three featured repository names from the spec, and no configured email/LinkedIn/portfolio URL.

- [ ] **Step 2: Run the happy-path test to verify it fails**

Run: `pytest tests/test_config.py::test_load_config_returns_validated_profile_config -v`

Expected: FAIL because `generator.config` does not exist.

- [ ] **Step 3: Write failing validation tests**

Add `test_load_config_rejects_missing_identity`, `test_load_config_rejects_duplicate_domain`, `test_load_config_rejects_unknown_featured_repository_shape`, and `test_load_config_rejects_non_hex_palette_color`; each writes one minimal invalid YAML file and asserts `ConfigError` contains the offending field path.

- [ ] **Step 4: Implement configuration models and loader**

Implement the dataclasses in `generator/models.py` and `load_config(path: Path) -> ProfileConfig` in `generator/config.py`. Keep bilingual strings explicit as `title_en`, `subtitle_pt`, `description_en`, and `description_pt`; validate required keys, unique domains, featured-project shape, and six-digit `#RRGGBB` palette values.

- [ ] **Step 5: Add the curated repository configuration and dependency files**

Create `config.yml` with the exact identity, stack, featured projects, and palette approved in the spec. Pin `PyYAML>=6.0,<7.0`, `pytest>=8.0,<9.0`, and `CairoSVG>=2.7,<3.0` in the appropriate requirements files.

- [ ] **Step 6: Run configuration tests**

Run: `pytest tests/test_config.py -v`

Expected: all configuration tests PASS.

- [ ] **Step 7: Commit Task 1**

```bash
git add config.yml requirements*.txt generator/__init__.py generator/models.py generator/config.py tests/test_config.py
git commit -m "feat: add profile configuration models"
```

### Task 2: Public GitHub data client

**Files:**
- Create: `generator/github_client.py`
- Create: `tests/fixtures/github-profile.json`
- Create: `tests/fixtures/github-profile-partial.json`
- Create: `tests/test_github_client.py`

**Interfaces:**
- Consumes: `FeaturedProject` names from `ProfileConfig`.
- Produces: dataclasses `RepositoryData` and `PublicProfileData` in `generator/models.py`; `GitHubApiError(RuntimeError)`; `fetch_public_profile(username: str, token: str, request_json: JsonRequester | None = None) -> PublicProfileData`, where `JsonRequester` is `Callable[[str, dict[str, object], str], dict[str, object]]`.

- [ ] **Step 1: Write the failing successful-response test**

Create `test_fetch_public_profile_normalizes_public_non_fork_data` with the success fixture containing two owned repositories, one fork, language byte counts, followers, and current-year contributions. Assert `public_repository_count == 2`, the fork is absent, `contributions_year == 58`, followers are preserved, unique language count is calculated from the two owned repositories, and repository lookup is keyed by exact repository name.

- [ ] **Step 2: Run the successful-response test to verify it fails**

Run: `pytest tests/test_github_client.py::test_fetch_public_profile_normalizes_public_non_fork_data -v`

Expected: FAIL because `fetch_public_profile` does not exist.

- [ ] **Step 3: Write failing partial and error response tests**

Add `test_fetch_public_profile_preserves_missing_metrics_as_none`, `test_fetch_public_profile_excludes_private_and_fork_nodes`, `test_fetch_public_profile_raises_on_graphql_errors`, and `test_fetch_public_profile_raises_on_malformed_payload`. Assert the error messages name `GitHub GraphQL API` without including the token.

- [ ] **Step 4: Implement the GraphQL client and normalized models**

Implement one query for `user(login:)`, `followers.totalCount`, `contributionsCollection.contributionCalendar.totalContributions`, and up to 100 owner repositories with `isFork`, visibility, URL, description, primary language, and language byte edges. Default transport uses `urllib.request` against `https://api.github.com/graphql`; the injected transport makes tests network-free. Filter private and fork nodes before calculating counts and language totals.

- [ ] **Step 5: Run client tests**

Run: `pytest tests/test_github_client.py -v`

Expected: all GitHub client tests PASS.

- [ ] **Step 6: Commit Task 2**

```bash
git add generator/models.py generator/github_client.py tests/fixtures tests/test_github_client.py
git commit -m "feat: collect public GitHub profile data"
```

### Task 3: SVG primitives and orbital header

**Files:**
- Create: `generator/svg.py`
- Create: `generator/templates/__init__.py`
- Create: `generator/templates/orbit_header.py`
- Create: `tests/test_svg_generation.py`

**Interfaces:**
- Consumes: `ProfileConfig` from Task 1.
- Produces: `escape_text(value: str) -> str`, `svg_document(*, width: int, height: int, title: str, body: str) -> str`, `validate_svg(svg: str) -> None`, and `render_orbit_header(config: ProfileConfig) -> str`.

- [ ] **Step 1: Write failing orbital-header tests**

Create `test_orbit_header_is_valid_accessible_svg` asserting XML parse success, `viewBox="0 0 850 300"`, a `<title>` element, `Nicolas Gabriel`, all four domain labels, and all configured technology names. Add `test_orbit_header_escapes_xml_sensitive_text` using the name `Nicolas & Gabriel <Dev>` and asserting parse success plus escaped source text.

- [ ] **Step 2: Run the orbital tests to verify they fail**

Run: `pytest tests/test_svg_generation.py -k orbit_header -v`

Expected: FAIL because the SVG modules do not exist.

- [ ] **Step 3: Implement shared SVG primitives**

Implement the exact public functions in `generator/svg.py` using `html.escape(..., quote=True)` and `xml.etree.ElementTree.fromstring` for validation. `svg_document` must include `role="img"`, `aria-labelledby`, one `<title>`, the configured dark background, and the 850-wide responsive coordinate system.

- [ ] **Step 4: Implement the original orbital header template**

Render a central `NG` node, four distinct labeled orbits for Mobile/Web/IoT/AWS, and technology nodes assigned from `config.yml`. Keep all text within x=40..810 and y=30..270; use the approved navy/cyan/violet/green/amber palette and no wording or coordinates copied from the reference profile.

- [ ] **Step 5: Run orbital and XML tests**

Run: `pytest tests/test_svg_generation.py -k 'orbit_header or escape or document' -v`

Expected: selected tests PASS.

- [ ] **Step 6: Commit Task 3**

```bash
git add generator/svg.py generator/templates tests/test_svg_generation.py
git commit -m "feat: render original orbital profile header"
```

### Task 4: Telemetry and stack-map panels

**Files:**
- Create: `generator/templates/telemetry.py`
- Create: `generator/templates/stack_map.py`
- Modify: `tests/test_svg_generation.py`

**Interfaces:**
- Consumes: `ProfileConfig` and `PublicProfileData` from Tasks 1–2; shared SVG functions from Task 3.
- Produces: `render_telemetry(config: ProfileConfig, profile: PublicProfileData) -> str` and `render_stack_map(config: ProfileConfig, profile: PublicProfileData) -> str`.

- [ ] **Step 1: Write failing telemetry tests**

Add `test_telemetry_renders_four_verified_public_metrics` asserting the labels `PUBLIC REPOS`, `CONTRIBUTIONS`, `FOLLOWERS`, and `LANGUAGES` with fixture values. Add `test_telemetry_uses_em_dash_for_none` asserting absent contributions and followers render `—`, not `0`.

- [ ] **Step 2: Run telemetry tests to verify they fail**

Run: `pytest tests/test_svg_generation.py -k telemetry -v`

Expected: FAIL because `render_telemetry` does not exist.

- [ ] **Step 3: Implement telemetry rendering**

Render four equal cells in an 850×180 SVG, one icon-like geometric mark per metric, bilingual section labeling (`MISSION TELEMETRY / TELEMETRIA`), and tabular values. Format values below 1000 as integers and larger values with one lowercase `k` decimal.

- [ ] **Step 4: Write failing stack-map tests**

Add `test_stack_map_contains_all_declared_domains_and_technologies`, `test_stack_map_uses_public_language_bytes_for_bar_proportions`, and `test_stack_map_keeps_declared_technologies_when_language_data_is_empty`. Assert every configured technology is present exactly once and all generated bar widths remain between 4 and 360.

- [ ] **Step 5: Run stack-map tests to verify they fail**

Run: `pytest tests/test_svg_generation.py -k stack_map -v`

Expected: FAIL because `render_stack_map` does not exist.

- [ ] **Step 6: Implement stack-map rendering**

Render an 850×330 SVG with a left language-telemetry column and a right four-domain system map. Normalize detected language bytes into bounded bars, then render all declared technologies from config even when no public language bytes map to them.

- [ ] **Step 7: Run all Task 4 tests**

Run: `pytest tests/test_svg_generation.py -k 'telemetry or stack_map' -v`

Expected: selected tests PASS.

- [ ] **Step 8: Commit Task 4**

```bash
git add generator/templates/telemetry.py generator/templates/stack_map.py tests/test_svg_generation.py
git commit -m "feat: add telemetry and technology panels"
```

### Task 5: Featured projects and atomic generation pipeline

**Files:**
- Create: `generator/templates/featured_projects.py`
- Create: `generator/main.py`
- Create: `tests/test_generation_pipeline.py`
- Modify: `tests/test_svg_generation.py`

**Interfaces:**
- Consumes: all earlier models, client, config loader, SVG primitives, and renderers.
- Produces: `render_featured_projects(config: ProfileConfig, profile: PublicProfileData) -> str`; `render_all(config: ProfileConfig, profile: PublicProfileData) -> dict[str, str]`; `publish_generated(rendered: Mapping[str, str], output_dir: Path) -> None`; CLI `python -m generator.main --config config.yml --output assets/generated [--fixture FILE]`.

- [ ] **Step 1: Write failing featured-project tests**

Add `test_featured_projects_uses_curated_bilingual_copy_and_public_urls` asserting all three configured titles, both language descriptions, domain labels, and matching GitHub URLs. Add `test_featured_projects_keeps_curated_card_when_remote_repository_is_missing` asserting the configured title and copy remain while unavailable remote details are omitted.

- [ ] **Step 2: Run featured-project tests to verify they fail**

Run: `pytest tests/test_svg_generation.py -k featured_projects -v`

Expected: FAIL because the template does not exist.

- [ ] **Step 3: Implement featured-project rendering**

Render an 850×300 SVG with three equal project cells, concise two-language descriptions, domain labels, and repository names. The SVG is informational; clickable repository links live in `README.md` for consistent GitHub rendering.

- [ ] **Step 4: Write failing generation-pipeline tests**

Create `test_render_all_returns_exact_four_valid_assets`, `test_fixture_cli_generates_all_assets`, `test_publish_generated_preserves_existing_assets_when_one_svg_is_invalid`, and `test_publish_generated_replaces_all_assets_after_full_validation`. Use `tmp_path`; preseed four sentinel SVGs for the failure test and assert every byte remains unchanged after `ValueError`.

- [ ] **Step 5: Run pipeline tests to verify they fail**

Run: `pytest tests/test_generation_pipeline.py -v`

Expected: FAIL because `generator.main` does not exist.

- [ ] **Step 6: Implement rendering, validation, and staged publication**

Implement `render_all` with the exact four filenames from Global Constraints. `publish_generated` must validate every string, write all four into a temporary sibling directory, fsync and close them, then replace published files only after the full staging pass succeeds. The CLI uses the fixture when supplied; otherwise it requires `GITHUB_TOKEN` and calls `fetch_public_profile`.

- [ ] **Step 7: Run featured and pipeline tests**

Run: `pytest tests/test_svg_generation.py tests/test_generation_pipeline.py -v`

Expected: all SVG and pipeline tests PASS.

- [ ] **Step 8: Commit Task 5**

```bash
git add generator/templates/featured_projects.py generator/main.py tests/test_svg_generation.py tests/test_generation_pipeline.py
git commit -m "feat: generate and publish profile assets safely"
```

### Task 6: Profile README and GitHub Actions automation

**Files:**
- Create: `README.md`
- Create: `.github/workflows/generate-profile.yml`
- Create: `tests/test_repository_contract.py`
- Create: `assets/generated/.gitkeep`

**Interfaces:**
- Consumes: the generator CLI and exact four filenames from Task 5.
- Produces: the public profile page contract and automated daily/manual/push regeneration workflow.

- [ ] **Step 1: Write failing README contract tests**

Create `test_readme_identifies_nicolas_bilingually`, `test_readme_references_exact_four_local_assets`, `test_readme_links_exact_three_featured_repositories`, and `test_readme_contains_no_unconfirmed_contact_links`. Assert all four asset paths exist after fixture generation.

- [ ] **Step 2: Run README contract tests to verify they fail**

Run: `pytest tests/test_repository_contract.py -k readme -v`

Expected: FAIL because `README.md` does not exist.

- [ ] **Step 3: Implement the bilingual README**

Create a centered introduction with the exact identity from Global Constraints, concise Portuguese context, focus labels, and accessible `<img>` elements for the four local SVGs at `width="850"`. Add plain Markdown links for the exact three featured repositories below the featured-project image. Do not add an email, LinkedIn, portfolio, years of experience, visitor counter, or third-party stats card.

- [ ] **Step 4: Write failing workflow contract tests**

Add `test_workflow_has_daily_manual_and_scoped_push_triggers`, `test_workflow_uses_python_312_and_github_token`, `test_workflow_grants_only_contents_write`, and `test_workflow_commits_only_when_git_diff_is_nonempty`. Parse the workflow as YAML and assert the push path filters exclude `assets/generated/**` to prevent a commit loop.

- [ ] **Step 5: Run workflow contract tests to verify they fail**

Run: `pytest tests/test_repository_contract.py -k workflow -v`

Expected: FAIL because the workflow does not exist.

- [ ] **Step 6: Implement the GitHub Actions workflow**

Configure `workflow_dispatch`, daily schedule `17 8 * * *`, and a `push` trigger limited to generator/config/test/workflow/requirements paths. Use Python 3.12, install both requirements files, run `pytest -q`, run `python -m generator.main`, and commit `assets/generated/*.svg` only when `git diff --quiet -- assets/generated` is false. Use `github-actions[bot]` identity and `[skip ci]` in the generated-assets commit.

- [ ] **Step 7: Generate the initial assets with the deterministic fixture**

Run: `python -m generator.main --config config.yml --output assets/generated --fixture tests/fixtures/github-profile.json`

Expected: exactly four non-empty valid SVG files are created.

- [ ] **Step 8: Run repository contract and full test suites**

Run: `pytest -q`

Expected: all tests PASS.

- [ ] **Step 9: Commit Task 6**

```bash
git add README.md .github/workflows/generate-profile.yml assets/generated tests/test_repository_contract.py
git commit -m "feat: add bilingual automated profile README"
```

### Task 7: Visual verification and GitHub publication

**Files:**
- Modify only if verification finds a defect: `generator/templates/*.py`, `config.yml`, `README.md`, or tests covering the defect.
- Remote create: `github.com/nicolas-takimo/nicolas-takimo`.

**Interfaces:**
- Consumes: complete tested local repository from Tasks 1–6 and authenticated `gh` account `nicolas-takimo`.
- Produces: public profile repository, successful workflow run, and verified GitHub profile rendering.

- [ ] **Step 1: Render desktop and mobile PNG previews**

Run a short test helper using `cairosvg.svg2png` for each SVG at output widths 850 and 360, writing previews to a task-owned temporary directory.

Expected: eight non-empty PNGs render without CairoSVG exceptions.

- [ ] **Step 2: Inspect every preview**

Open the eight PNGs and verify no label is clipped or overlaps, all four domains are distinguishable without color alone, bilingual copy is legible, and the 360px render remains understandable. Any defect requires a failing regression test, minimal template correction, full `pytest -q`, and a focused fix commit before continuing.

- [ ] **Step 3: Run pre-publication verification**

Run: `pytest -q && git diff --check && git status --short`

Expected: tests PASS, `git diff --check` is silent, and the only status is a clean `main` branch.

- [ ] **Step 4: Confirm the remote target is still absent**

Run: `gh repo view nicolas-takimo/nicolas-takimo --json nameWithOwner,visibility 2>&1`

Expected: repository not found. If it exists, stop and inspect it before changing remote state.

- [ ] **Step 5: Create and push the public profile repository**

Run: `gh repo create nicolas-takimo/nicolas-takimo --public --source=. --remote=origin --push --description "Computer Engineer · Full-Stack Developer · Mobile · Web · IoT · AWS"`

Expected: remote repository is created and local `main` tracks `origin/main`.

- [ ] **Step 6: Trigger and follow the generator workflow**

Run: `gh workflow run generate-profile.yml --repo nicolas-takimo/nicolas-takimo` followed by `gh run watch --repo nicolas-takimo/nicolas-takimo --exit-status` for the dispatched run ID.

Expected: workflow concludes with `success` and, if live public data differs from fixtures, creates one `[skip ci]` asset update commit.

- [ ] **Step 7: Pull the generated update and verify remote state**

Run: `git pull --ff-only && gh repo view nicolas-takimo/nicolas-takimo --json url,visibility,defaultBranchRef`

Expected: visibility is `PUBLIC`, default branch is `main`, and local state is clean.

- [ ] **Step 8: Verify the public profile README**

Open `https://github.com/nicolas-takimo` and confirm the profile README is visible, all four local SVGs load, the three project links resolve, and no private or unconfirmed information appears.

- [ ] **Step 9: Record the publication result**

Report the repository URL, workflow run URL, final test count, and any follow-up item that was deliberately left outside the approved scope.
