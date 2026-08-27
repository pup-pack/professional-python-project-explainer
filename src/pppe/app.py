"""app.py - interactive explainer.

Author: Denise Case
Date: 2026-08

Run from the repository root with:

    uv run marimo run src/pppe/app.py

Edit with:

    uv run marimo edit src/pppe/app.py

REQUIREMENTS:

1. Add marimo to notebooks in pyproject.toml
2. Install the required dependencies using `uv sync`.

ABOUT THE FILE OPENING ABOVE:

Marimo's WASM dependency mechanism
uses the notebook's PEP 723 metadata.
Marimo's current WASM guidance says that
without a script block first, imported packages
do not auto-install in WASM.

NO LOGGING:

In this notebook, we do not configure logging because a browser-based
WASM app has no persistent Python server to store log files.

DATA FILES (in public/):

- repos.toml       the list of repository URLs shown in the dropdown
- annotations.toml the reusable, repository-independent catalog that
                   describes common files and folders (description,
                   rationale, and whether to highlight)
- data.toml        app metadata (the title)

The repository tree itself is NOT stored. When a repository is selected,
its file and folder list is fetched live from the GitHub trees API and
joined against annotations.toml. Fetches use the same urllib path that
loads the TOML files, which marimo patches for WASM via pyodide-http.
Unauthenticated GitHub requests are limited to 60 per hour per IP, so
successful fetches are cached and failures surface a clear message.

FIRST: IMPORT AND APP SETUP (ALWAYS)

THEN: PLAN CELLS FIRST - I want these cells:

1. _imports
2. _load_static_data
3. _choose_repository
4. _get_selected_repository
5. _track_selected_path
6. _choose_file_scope
7. _load_repository_tree
8. _build_tree_panel
9. _build_details_panel
10. _display_app

Note: No need to call @app.cell functions in marimo,
it triggers them automagically.
I could name them all "_", but I choose to
give them internal function names starting with "_"
so I can organize my thinking and my app.
"""

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="full")


@app.cell
def _imports():
    import marimo as mo

    from pppe.app_core import (
        RepoTreeError,
        build_tree_items,
        fetch_repo_tree,
        filter_items,
        get_item_by_path,
        get_repo_name,
        get_tree_label,
        index_items_by_path,
        load_annotations,
        load_project_meta,
        load_repo_list,
    )

    return (
        RepoTreeError,
        build_tree_items,
        fetch_repo_tree,
        filter_items,
        get_item_by_path,
        get_repo_name,
        get_tree_label,
        index_items_by_path,
        load_annotations,
        load_project_meta,
        load_repo_list,
        mo,
    )


@app.cell
def _load_static_data(
    load_annotations,
    load_project_meta,
    load_repo_list,
    mo,
):
    notebook_location = mo.notebook_location()
    if notebook_location is None:
        raise RuntimeError("Unable to determine notebook location.")

    public_path = notebook_location / "public"
    project_data_path = public_path / "data.toml"
    repo_data_path = public_path / "repos.toml"
    annotations_path = public_path / "explainer-catalog.toml"

    project = load_project_meta(project_data_path)
    repo_urls = load_repo_list(repo_data_path)
    annotations = load_annotations(annotations_path)

    return annotations, project, repo_urls


@app.cell
def _choose_repository(get_repo_name, mo, repo_urls):
    repo_options = {get_repo_name(repo_url): repo_url for repo_url in repo_urls}
    first_repo_name = get_repo_name(repo_urls[0])

    repo_selector = mo.ui.dropdown(
        options=repo_options,
        value=first_repo_name,
        label="Repository",
        full_width=True,
    )

    return (repo_selector,)


@app.cell
def _get_selected_repository(get_repo_name, repo_selector):
    if repo_selector.value is None:
        raise RuntimeError("No repository is selected.")

    selected_repo_url = str(repo_selector.value)
    selected_repo_name = get_repo_name(selected_repo_url)

    return selected_repo_name, selected_repo_url


@app.cell
def _track_selected_path(mo):
    get_selected_path, set_selected_path = mo.state("README.md")
    return get_selected_path, set_selected_path


@app.cell
def _choose_file_scope(mo):
    show_all = mo.ui.switch(
        value=False,
        label="Show all files",
    )
    return (show_all,)


@app.cell
def _load_repository_tree(
    RepoTreeError,
    annotations,
    build_tree_items,
    fetch_repo_tree,
    index_items_by_path,
    selected_repo_name,
    selected_repo_url,
):
    try:
        entries = fetch_repo_tree(selected_repo_url)
        items = build_tree_items(
            repo_name=selected_repo_name,
            entries=entries,
            annotations=annotations,
        )
        tree_error = None
    except RepoTreeError as error:
        items = []
        tree_error = str(error)

    items_by_path = index_items_by_path(items)

    return items, items_by_path, tree_error


@app.cell
def _build_tree_panel(
    filter_items,
    get_tree_label,
    items,
    mo,
    selected_repo_name,
    set_selected_path,
    show_all,
    tree_error,
):
    def make_tree_button(item):
        path = str(item["path"])
        attention = bool(item["attention"])

        button = mo.ui.button(
            label=get_tree_label(item),
            kind="warn" if attention else "neutral",
            tooltip=str(item["description"]),
            on_click=lambda _value, selected=path: (
                set_selected_path(selected),
                selected,
            )[1],
        )

        return mo.hstack(
            [button],
            justify="start",
        )

    if tree_error is not None:
        tree_body = mo.md(
            f"**Could not load this repository.**\n\n{tree_error}"
        ).callout(
            kind="danger",
        )
    else:
        visible_items = filter_items(
            items,
            highlighted_only=not show_all.value,
        )
        tree_rows = [make_tree_button(item) for item in visible_items]
        tree_body = mo.vstack(tree_rows, gap=0.08).style(
            max_height="70vh",
            overflow="auto",
            padding="0.25rem",
        )

    tree_panel = mo.vstack(
        [
            mo.md(
                rf"""
## {selected_repo_name}

**Highlighted entries hold key project-specific content.**
"""
            ),
            show_all,
            tree_body,
        ],
        gap=0.5,
    )

    return (tree_panel,)


@app.cell
def _build_details_panel(
    get_selected_path,
    items_by_path,
    mo,
    selected_repo_url,
):
    selected_path = get_selected_path()
    selected = items_by_path.get(selected_path) or items_by_path.get(".")

    if selected is None:
        details_panel = mo.md(
            "Select a repository to see file and folder details."
        ).callout(kind="neutral")
    else:
        details_panel = mo.md(
            rf"""
## `{selected["path"]}`

---

### Description

{selected["description"]}

---

### Rationale

{selected["rationale"]}

---

[**🔗 View in selected repository**]({selected_repo_url})
"""
        ).callout(kind="warn" if selected["attention"] else "neutral")

    return (details_panel,)


@app.cell
def _display_app(
    details_panel,
    mo,
    project,
    repo_selector,
    tree_panel,
):
    mo.vstack(
        [
            mo.md(
                rf"""
# {project["title"]}

A Marimo app that explains common files and folders in a professional Python project.
Each entry is **clickable**; highlighted entries hold key project-specific content.
[🔗 View source](https://github.com/pup-pack/professional-python-project-explainer).

---
"""
            ),
            repo_selector,
            mo.hstack(
                [tree_panel, details_panel],
                widths=[1.15, 1.0],
                align="start",
                wrap=True,
                gap=1.25,
            ),
        ],
        gap=1.0,
    )


if __name__ == "__main__":
    app.run()
