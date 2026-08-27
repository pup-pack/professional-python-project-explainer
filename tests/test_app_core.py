"""Tests for pppe.app_core."""

from pathlib import Path
from typing import Any

from pppe.app_core import (
    build_tree_items,
    filter_items,
    get_item_by_path,
    get_repo_name,
    get_repo_slug,
    index_items_by_path,
    load_annotations,
    load_project_meta,
    load_repo_list,
    resolve_annotation,
)

PUBLIC_DIR = Path(__file__).parents[1] / "src" / "pppe" / "public"


def make_annotations() -> dict[str, Any]:
    return {
        "root": {
            "attention": False,
            "description": "Repository root.",
            "rationale": "Contains the project.",
        },
        "defaults": {
            "file": {
                "attention": False,
                "description": "Project file.",
                "rationale": "Part of the project.",
            },
            "directory": {
                "attention": False,
                "description": "Project directory.",
                "rationale": "Groups related files.",
            },
        },
        "paths": {
            "src/pppe/app.py": {
                "attention": True,
                "description": "Exact application module.",
                "rationale": "Runs the application.",
            },
        },
        "directories": {
            "data": {
                "attention": True,
                "description": "Data directory.",
                "rationale": "Contains project data.",
            },
        },
        "names": {
            "README.md": {
                "attention": True,
                "description": "Project readme.",
                "rationale": "Introduces the project.",
            },
        },
        "globs": [
            {
                "match": "src/*.py",
                "attention": True,
                "description": "Python source module.",
                "rationale": "Contains project code.",
            },
        ],
    }


def test_repo_url_helpers() -> None:
    repo_url = "https://github.com/denisecase/datafun-01-foundations"

    assert get_repo_name(repo_url) == "datafun-01-foundations"
    assert get_repo_slug(repo_url) == "denisecase/datafun-01-foundations"


def test_annotation_resolution_precedence() -> None:
    annotations = make_annotations()

    exact = resolve_annotation(
        annotations,
        path="src/pppe/app.py",
        is_dir=False,
    )
    named = resolve_annotation(
        annotations,
        path="README.md",
        is_dir=False,
    )
    globbed = resolve_annotation(
        annotations,
        path="src/pppe/utils.py",
        is_dir=False,
    )
    directory = resolve_annotation(
        annotations,
        path="data",
        is_dir=True,
    )
    default = resolve_annotation(
        annotations,
        path="unknown.txt",
        is_dir=False,
    )

    assert exact["description"] == "Exact application module."
    assert named["description"] == "Project readme."
    assert globbed["description"] == "Python source module."
    assert directory["description"] == "Data directory."
    assert default["description"] == "Project file."


def test_tree_is_sorted_alphabetically() -> None:
    entries = (
        ("README.md", False),
        ("data", True),
        ("data/z.csv", False),
        ("data/A.csv", False),
        ("src", True),
        ("src/pppe", True),
        ("src/pppe/app.py", False),
    )

    items = build_tree_items(
        repo_name="example-project",
        entries=entries,
        annotations=make_annotations(),
    )

    lines = [str(item["line"]) for item in items]

    assert lines == [
        "example-project/",
        "├── data/",
        "│   ├── A.csv",
        "│   └── z.csv",
        "├── README.md",
        "└── src/",
        "    └── pppe/",
        "        └── app.py",
    ]


def test_filter_and_index_items() -> None:
    items = build_tree_items(
        repo_name="example-project",
        entries=(
            ("README.md", False),
            ("uv.lock", False),
        ),
        annotations=make_annotations(),
    )

    items_by_path = index_items_by_path(items)
    highlighted = filter_items(
        items,
        highlighted_only=True,
    )

    assert get_item_by_path(items_by_path, "README.md")["attention"] is True
    assert get_item_by_path(items_by_path, "uv.lock")["attention"] is False
    assert [item["path"] for item in highlighted] == ["README.md"]


def test_public_toml_files_load() -> None:
    project = load_project_meta(PUBLIC_DIR / "data.toml")
    repo_urls = load_repo_list(PUBLIC_DIR / "repos.toml")
    annotations = load_annotations(PUBLIC_DIR / "explainer-catalog.toml")

    assert project["title"]
    assert repo_urls
    assert all(url.startswith("https://github.com/") for url in repo_urls)
    assert annotations["defaults"]["file"]["description"]
    assert annotations["defaults"]["directory"]["description"]
