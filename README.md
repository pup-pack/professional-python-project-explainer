# Professional Python Project Explainer

[![Live App](https://img.shields.io/badge/open-live%20app-brightgreen)](https://pup-pack.github.io/professional-python-project-explainer/)
[![marimo](https://img.shields.io/badge/marimo-reactive%20app-orange)](https://marimo.io/)

[![Python 3.14](https://img.shields.io/badge/python-3.14%2B-blue?logo=python)](./pyproject.toml)
[![uv managed](https://img.shields.io/badge/uv-managed-DE5FE9)](https://docs.astral.sh/uv/)
[![ty type checked](https://img.shields.io/badge/ty-type_checked-2F80ED)](https://docs.astral.sh/ty/)
[![MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](https://github.com/pup-pack/professional-python-project-explainer/blob/main/LICENSE)

> A Marimo app that explains common files and folders in current public GitHub repositories.

## Open the App

- [Professional Python Project Explainer](https://pup-pack.github.io/professional-python-project-explainer/)

## How It Works

- Repository choices are loaded from `src/pppe/public/repos.toml`.
- The selected repository tree is fetched live from GitHub.
- Common files and folders are explained using `src/pppe/public/explainer-catalog.toml`.
- The repository tree is not stored and reflects the current repository shape.

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

# check types and run tests
uv run ty check
uv run python -m pytest

# save progress
git add -A
git commit -m "update"
git push -u origin main
```

</details>

## Explainer Catalog

[Explainer Catalog](src/pppe/public/annoexplainer-catalogtations.toml)

## Annotations

[Annotations](.annotations/annotations.md)

## Citation

[CITATION.cff](./CITATION.cff))

## License

[MIT](./LICENSE)
