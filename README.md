# Professional Python Project Explainer

[![Live App](https://img.shields.io/badge/open-live%20app-brightgreen)](https://pup-pack.github.io/professional-python-project-explainer/)
[![marimo](https://img.shields.io/badge/marimo-reactive%20app-orange)](https://marimo.io/)

[![Python 3.14](https://img.shields.io/badge/python-3.14%2B-blue?logo=python)](./pyproject.toml)
[![uv managed](https://img.shields.io/badge/uv-managed-DE5FE9)](https://docs.astral.sh/uv/)
[![ty type checked](https://img.shields.io/badge/ty-type_checked-2F80ED)](https://docs.astral.sh/ty/)
[![Zensical docs](https://img.shields.io/badge/Zensical-docs-purple)](https://zensical.org/)
[![MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](https://github.com/pup-pack/pup-clean/blob/main/LICENSE)

> A Marimo app that explains common files and folders in a professional Python project.

## Open the App

- [Professional Python Project Explorer](https://pup-pack.github.io/professional-python-project-explainer/)

## Run

```powershell
uv sync
uv run marimo run src/pppe/app.py
```

## Edit

```powershell
uv run marimo edit src/pppe/app.py
```

## Developer Command Reference

<details>
<summary>Show command reference</summary>

### In a machine terminal

Open a machine terminal where you want the project:

```shell
git clone https://github.com/pup-pack/professional-python-project-explainer

cd professional-python-project-explainer
code .
```

### In a VS Code terminal

```shell
uv self update
uv python pin 3.14
uv python install
uv lock --upgrade
uv sync

uv run pre-commit install
uv run pre-commit autoupdate

git add -A
uv run pre-commit run --all-files
# repeat if changes were made
uv run pre-commit run --all-files

# run locally to test
uv run marimo run src/pppe/app.py

# types, tests, docs
uv run ty check
uv run python -m pytest
uv run python -m zensical build

# save progress
git add -A
git commit -m "update"
git push -u origin main
```

</details>

## Documentation

- [Documentation](https://pup-pack.github.io/professional-python-project-explainer/)

## Annotations

[.annotations/annotations.md](.annotations/annotations.md)

## Citation

[CITATION.cff](CITATION.cff)

## License

[MIT](LICENSE)
