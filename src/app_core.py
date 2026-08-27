"""app_core.py - reusable logic."""

from fnmatch import fnmatchcase
from functools import lru_cache
import json
import os
from pathlib import Path, PurePath
import tomllib
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

__all__ = [
    "RepoTreeError",
    "build_tree_items",
    "fetch_repo_tree",
    "filter_items",
    "get_item_by_path",
    "get_repo_name",
    "get_repo_slug",
    "get_tree_label",
    "index_items_by_path",
    "load_annotations",
    "load_project_meta",
    "load_repo_list",
    "resolve_annotation",
    "resolve_root_annotation",
]

_GITHUB_API = "https://api.github.com"
_USER_AGENT = "professional-python-project-explainer"
_API_VERSION = "2022-11-28"
_REF_FALLBACKS = ("main", "master")


class RepoTreeError(RuntimeError):
    """Raised when a repository tree cannot be fetched from GitHub."""


def _load_toml(data_path: Path | PurePath | str) -> dict[str, Any]:
    """Load a TOML document from a local path or an http(s) URL.

    Args:
        data_path: The path or URL to the TOML file.

    Returns:
        The parsed TOML document.
    """
    location = str(data_path)

    if location.startswith(("http://", "https://")):
        with urlopen(location) as response:
            return tomllib.loads(response.read().decode("utf-8"))

    with Path(location).open("rb") as file:
        return tomllib.load(file)


def filter_items(
    items: list[dict[str, Any]],
    *,
    highlighted_only: bool,
) -> list[dict[str, Any]]:
    """Return all items or only highlighted items.

    Args:
        items: A list of project structure items.
        highlighted_only: If True, return only items with attention.

    Returns:
        A list of project structure items.
    """
    if not highlighted_only:
        return items

    return [item for item in items if bool(item["attention"])]


def get_item_by_path(
    items_by_path: dict[str, dict[str, Any]],
    path: str,
) -> dict[str, Any]:
    """Return the project structure item for a path.

    Args:
        items_by_path: A dictionary mapping paths to project structure items.
        path: The path of the project structure item to retrieve.

    Returns:
        The project structure item corresponding to the given path.
    """
    return items_by_path[path]


def get_repo_name(repo_url: str) -> str:
    """Return the repository name from a GitHub repository URL.

    Args:
        repo_url: The URL of the GitHub repository.

    Returns:
        The name of the repository.
    """
    return repo_url.rstrip("/").removesuffix(".git").rsplit("/", maxsplit=1)[-1]


def get_repo_slug(repo_url: str) -> str:
    """Return the ``owner/name`` slug from a GitHub repository URL.

    Args:
        repo_url: The URL of the GitHub repository.

    Returns:
        The ``owner/name`` slug used by the GitHub REST API.
    """
    trimmed = repo_url.rstrip("/").removesuffix(".git")
    parts = trimmed.split("/")

    if len(parts) < 2:
        raise ValueError(f"Cannot determine owner/name from URL: {repo_url}")

    return "/".join(parts[-2:])


def get_tree_label(item: dict[str, Any]) -> str:
    """Return the Markdown label for a project structure item.

    Args:
        item: A project structure item.

    Returns:
        The Markdown label for the project structure item.
    """
    line = str(item["line"])
    attention = bool(item["attention"])

    return f"**`{line}`**" if attention else f"`{line}`"


def index_items_by_path(
    items: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Index project structure items by path.

    Args:
        items: A list of project structure items.

    Returns:
        A dictionary mapping paths to project structure items.
    """
    return {str(item["path"]): item for item in items}


def load_project_meta(
    data_path: Path | PurePath | str,
) -> dict[str, Any]:
    """Load project metadata (such as the app title) from TOML.

    Args:
        data_path: The path to the TOML file containing the ``[project]`` table.

    Returns:
        The project metadata dictionary.
    """
    return _load_toml(data_path)["project"]


def load_repo_list(
    data_path: Path | PurePath | str,
) -> list[str]:
    """Load the repository URL list from TOML.

    Args:
        data_path: The path to the TOML file containing the repository URLs.

    Returns:
        A list of repository URLs as strings.
    """
    repo_data = _load_toml(data_path)
    return [str(url) for url in repo_data["repos"]["urls"]]


def load_annotations(
    data_path: Path | PurePath | str,
) -> dict[str, Any]:
    """Load the reusable annotation catalog from TOML.

    The catalog is repository-independent: it describes common files and folders
    (matched by exact path, directory name, file basename, or glob) so any
    repository tree can be joined against it.

    Args:
        data_path: The path to the annotation-catalog TOML file.

    Returns:
        A normalized annotation catalog.
    """
    raw = _load_toml(data_path)

    defaults = raw.get("defaults", {})

    return {
        "root": raw.get("root"),
        "defaults": {
            "file": defaults.get("file", {}),
            "directory": defaults.get("directory", {}),
        },
        "paths": dict(raw.get("paths", {})),
        "directories": dict(raw.get("directories", {})),
        "names": dict(raw.get("names", {})),
        "globs": list(raw.get("globs", [])),
    }


def _complete(
    entry: dict[str, Any],
    default: dict[str, Any],
) -> dict[str, Any]:
    """Return an annotation with attention, description, and rationale filled.

    Args:
        entry: The matched annotation entry.
        default: The applicable default annotation (file or directory).

    Returns:
        A complete annotation dictionary.
    """
    return {
        "attention": bool(entry.get("attention", False)),
        "description": str(
            entry.get("description", default.get("description", "")),
        ),
        "rationale": str(
            entry.get("rationale", default.get("rationale", "")),
        ),
    }


def resolve_annotation(
    annotations: dict[str, Any],
    *,
    path: str,
    is_dir: bool,
) -> dict[str, Any]:
    """Resolve the annotation for one repository path.

    Precedence, most specific first: exact path, directory name (directories
    only), file basename, glob (in listed order), then the file or directory
    default.

    Args:
        annotations: A normalized annotation catalog from ``load_annotations``.
        path: The repository-relative POSIX path.
        is_dir: Whether the path is a directory.

    Returns:
        A complete annotation dictionary (attention, description, rationale).
    """
    basename = path.rsplit("/", maxsplit=1)[-1]
    default = annotations["defaults"]["directory" if is_dir else "file"]

    candidates: list[dict[str, Any] | None] = [
        annotations["paths"].get(path),
        annotations["directories"].get(basename) if is_dir else None,
        annotations["names"].get(basename),
        _first_glob_match(annotations["globs"], path),
    ]

    for candidate in candidates:
        if candidate is not None:
            return _complete(candidate, default)

    return _complete(default, default)


def _first_glob_match(
    globs: list[dict[str, Any]],
    path: str,
) -> dict[str, Any] | None:
    """Return the first glob rule whose pattern matches a path.

    Note:
        Patterns use ``fnmatch`` semantics, where ``*`` also spans ``/``. So
        ``src/*.py`` matches ``src/datafun/app.py``.

    Args:
        globs: The ordered list of glob rules.
        path: The repository-relative POSIX path.

    Returns:
        The first matching glob rule, or None.
    """
    for rule in globs:
        pattern = str(rule.get("match", ""))

        if pattern and fnmatchcase(path, pattern):
            return rule

    return None


def resolve_root_annotation(
    annotations: dict[str, Any],
    *,
    repo_name: str,
) -> dict[str, Any]:
    """Resolve the annotation for the repository root.

    Args:
        annotations: A normalized annotation catalog from ``load_annotations``.
        repo_name: The repository name (used only if the catalog omits a root).

    Returns:
        A complete annotation dictionary for the root directory.
    """
    default = annotations["defaults"]["directory"]
    root = annotations["root"]

    if root is not None:
        return _complete(root, default)

    builtin = {
        "attention": False,
        "description": f"Root directory of the {repo_name} repository.",
        "rationale": (
            "Keeps code, data, documentation, tests, configuration, and "
            "automation together in one version-controlled project."
        ),
    }
    return _complete(builtin, default)


def _github_headers() -> dict[str, str]:
    """Return request headers for the GitHub REST API.

    Returns:
        Request headers, including an authorization token when available.
    """
    headers = {
        "User-Agent": _USER_AGENT,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": _API_VERSION,
    }

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

    if token:
        headers["Authorization"] = f"Bearer {token}"

    return headers


def _fetch_tree_payload(slug: str, ref: str) -> dict[str, Any]:
    """Fetch one recursive git-tree payload from the GitHub REST API.

    Args:
        slug: The ``owner/name`` repository slug.
        ref: The git ref (branch, tag, commit, or ``HEAD``).

    Returns:
        The parsed git-tree payload.

    Raises:
        HTTPError: If the request fails with an HTTP status.
        URLError: If the request fails at the network layer.
        RepoTreeError: If the response cannot be parsed as JSON.
    """
    url = f"{_GITHUB_API}/repos/{slug}/git/trees/{ref}?recursive=1"
    request = Request(url, headers=_github_headers())

    with urlopen(request, timeout=30) as response:
        raw = response.read().decode("utf-8")

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RepoTreeError(f"GitHub returned invalid JSON for {slug}.") from exc


@lru_cache(maxsize=128)
def fetch_repo_tree(
    repo_url: str,
    *,
    ref: str = "HEAD",
) -> tuple[tuple[str, bool], ...]:
    """Fetch a repository's recursive file and folder tree from GitHub.

    Successful results are cached for the process lifetime to conserve the
    unauthenticated GitHub rate limit (60 requests per hour per IP).

    Args:
        repo_url: The URL of the GitHub repository.
        ref: The git ref to read; falls back to ``main`` then ``master``.

    Returns:
        A tuple of ``(path, is_dir)`` pairs, sorted by path.

    Raises:
        RepoTreeError: If the tree cannot be fetched (for example, when the
            unauthenticated rate limit is exhausted).
    """
    slug = get_repo_slug(repo_url)

    refs: list[str] = [ref]
    refs.extend(candidate for candidate in _REF_FALLBACKS if candidate != ref)

    last_error: Exception | None = None

    for candidate_ref in refs:
        try:
            payload = _fetch_tree_payload(slug, candidate_ref)
        except HTTPError as exc:
            if exc.code == 403 and exc.headers.get("X-RateLimit-Remaining") == "0":
                raise RepoTreeError(
                    "GitHub's rate limit is exhausted for this network "
                    "(60 requests per hour when unauthenticated). "
                    "Please wait and try again.",
                ) from exc

            if exc.code in {404, 409, 422}:
                last_error = exc
                continue

            raise RepoTreeError(
                f"GitHub request failed for {slug} ({exc.code}).",
            ) from exc
        except URLError as exc:
            raise RepoTreeError(
                f"Could not reach GitHub for {slug}.",
            ) from exc

        entries = payload.get("tree")

        if not isinstance(entries, list):
            last_error = RepoTreeError(
                f"GitHub returned no tree for {slug} at {candidate_ref!r}.",
            )
            continue

        return _to_entry_pairs(entries)

    raise RepoTreeError(
        f"Could not fetch a tree for {slug}.",
    ) from last_error


def _to_entry_pairs(
    entries: list[dict[str, Any]],
) -> tuple[tuple[str, bool], ...]:
    """Convert raw git-tree entries into sorted ``(path, is_dir)`` pairs.

    Args:
        entries: Raw git-tree entries from the GitHub REST API.

    Returns:
        A tuple of ``(path, is_dir)`` pairs, sorted by path.
    """
    pairs = [
        (str(entry["path"]), entry.get("type") == "tree")
        for entry in entries
        if entry.get("path")
    ]
    return tuple(sorted(pairs, key=lambda pair: pair[0]))


def _render_tree_lines(
    entries: tuple[tuple[str, bool], ...],
) -> list[tuple[str, str]]:
    """Render tree-drawing lines for a set of repository entries.

    Args:
        entries: A tuple of ``(path, is_dir)`` pairs.

    Returns:
        A list of ``(path, line)`` pairs in display order, where each line uses
        the same box-drawing style as the tree output of the ``tree`` command.
    """
    is_dir = dict(entries)
    children: dict[str, list[str]] = {}

    for path, _ in entries:
        parent = path.rsplit("/", maxsplit=1)[0] if "/" in path else ""
        children.setdefault(parent, []).append(path)
        children.setdefault(path, children.get(path, []))

    for siblings in children.values():
        siblings.sort(key=lambda path: path.rsplit("/", maxsplit=1)[-1].casefold())

    lines: list[tuple[str, str]] = []

    def walk(parent: str, prefix: str) -> None:
        siblings = children.get(parent, [])

        for index, path in enumerate(siblings):
            is_last = index == len(siblings) - 1
            connector = "└── " if is_last else "├── "
            name = path.rsplit("/", maxsplit=1)[-1]
            suffix = "/" if is_dir.get(path) else ""

            lines.append((path, f"{prefix}{connector}{name}{suffix}"))
            walk(path, prefix + ("    " if is_last else "│   "))

    walk("", "")
    return lines


def build_tree_items(
    *,
    repo_name: str,
    entries: tuple[tuple[str, bool], ...],
    annotations: dict[str, Any],
) -> list[dict[str, Any]]:
    """Combine a repository tree with annotations into display items.

    Args:
        repo_name: The repository name (used for the root label).
        entries: A tuple of ``(path, is_dir)`` pairs from ``fetch_repo_tree``.
        annotations: A normalized annotation catalog from ``load_annotations``.

    Returns:
        A list of display items, each with path, line, attention, description,
        and rationale, in display order and starting with the repository root.
    """
    is_dir = dict(entries)

    items: list[dict[str, Any]] = [
        {
            "path": ".",
            "line": f"{repo_name}/",
            **resolve_root_annotation(annotations, repo_name=repo_name),
        },
    ]

    for path, line in _render_tree_lines(entries):
        annotation = resolve_annotation(
            annotations,
            path=path,
            is_dir=is_dir[path],
        )
        items.append({"path": path, "line": line, **annotation})

    return items
