# Changelog

<!-- markdownlint-disable MD024 -->

All notable changes to this project will be documented in this file.

The format is based on **[Keep a Changelog](https://keepachangelog.com/en/1.1.0/)**
and this project adheres to **[Semantic Versioning](https://semver.org/spec/v2.0.0.html)**.

---

## [Unreleased]

---

## [0.1.1] - 2026-10-10

### Changed

- changed from `.pre-commit-config.yaml` to `prek.toml`
- professional python update with `uvx pup-up@latest`.
- added project `docs` and `zensical.toml`

---

## [0.1.0] - 2026-08-27

### Added

- Initial Professional Python Project Explainer.
- Interactive Marimo interface for exploring professional Python repositories.
- Repository selector backed by a reusable TOML repository list.
- Live repository file and folder trees retrieved from GitHub.
- Reusable explainer catalog for common project files and directories.
- Highlighted project-specific content.
- Clickable tree entries with descriptions and rationales.
- WebAssembly deployment support.

---

## Notes on Versioning and Releases

- We use **SemVer**:
  - **MAJOR** - breaking changes
  - **MINOR** - backward-compatible additions
  - **PATCH** - fixes, documentation, tooling
- Versions are driven by git tags.
- Tag `vX.Y.Z` to release.
- Docs are deployed per version tag and aliased to **latest**.

## Release Procedure

Follow these steps when creating a new release.

### Task 1. Update release metadata

1. Update `CITATION.cff`: change `version` and `date-released`
2. Update `CHANGELOG.md`: move from unreleased, add entry, update links
3. Update `pyproject.toml`: update `project.version`

### Task 2. Validate

```shell
.\sit.ps1

# Update GitHub Actions and pin all action references to immutable SHAs
uvx gha-tools autoupdate --pin=all --write .github/workflows

# Then audit the resulting GitHub configuration for security findings
uvx zizmor@latest .github/

# Run checks
uvx cffconvert --validate
npx markdownlint-cli2 --fix

# run the app
uv run marimo run src/app.py

# Generate the Marimo application inside the Zensical source tree
uv run marimo export html-wasm src/app.py -o docs/app --mode run
# Type y to overwrite as needed

# Verify the exported application
Test-Path docs/app/index.html
Test-Path docs/app/public/data.toml

# Build the complete website
uv run python -m zensical build

# Verify both entry points
Test-Path site/index.html
Test-Path site/app/index.html
```

### Task 3. Commit, push, tag

```shell
git add -A
git commit -m "Prepare X.Y.Z"
git push -u origin main
```

Verify actions run on GitHub. After success:

```shell
git tag vX.Y.Z -m "X.Y.Z"
git push origin vX.Y.Z
```

## Only As Needed (delete a tag)

```shell
git tag -d vX.Z.Y
git push origin :refs/tags/vX.Z.Y
```

## Links

[Unreleased]: https://github.com/pup-pack/professional-python-project-explainer/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/pup-pack/professional-python-project-explainer/releases/tag/v0.1.1
[0.1.0]: https://github.com/pup-pack/professional-python-project-explainer/releases/tag/v0.1.0

<!-- markdownlint-enable MD024 -->
