"""Lazy file tree with filters and explicit filesystem operations."""
from __future__ import annotations

import os
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class TreeNode:
    """A filesystem entry; symlink directories are never traversed."""
    path: Path
    is_dir: bool
    children: list[TreeNode] = field(default_factory=list)
    expanded: bool = False
    has_md: bool = False


class TreeView:
    """Browse one directory root without recursively scanning large trees."""

    def __init__(self, root: Path, hidden: bool = False, sort: str = "alpha") -> None:
        self.root = TreeNode(root.resolve(), True, expanded=True)
        self.hidden = hidden
        self.sort = sort
        self.pattern: Optional[re.Pattern] = None
        self.cursor_index = 0
        self.visible_nodes: list[tuple[TreeNode, int]] = []
        self.errors: list[str] = []
        self.cache: dict[Path, tuple[int, list[TreeNode]]] = {}
        self.refresh()

    @property
    def current(self) -> TreeNode:
        """Return selected node or root when empty."""
        return self.visible_nodes[self.cursor_index][0] if self.visible_nodes else self.root

    def _children(self, node: TreeNode) -> list[TreeNode]:
        try:
            stamp = node.path.stat().st_mtime_ns
            cached = self.cache.get(node.path)
            if not cached or cached[0] != stamp:
                old = {n.path: n for n in node.children}
                children = []
                for path in node.path.iterdir():
                    is_dir = path.is_dir() and not path.is_symlink()
                    if is_dir or path.suffix.lower() in (".md", ".markdown", ".txt"):
                        children.append(old.get(path) or TreeNode(path, is_dir))
                self.cache[node.path] = stamp, children
            node.children = self.cache[node.path][1]
        except OSError as exc:
            self.errors.append(str(exc))
            node.children = []
        children = [n for n in node.children if self.hidden or not n.path.name.startswith(".")]
        def key(n: TreeNode) -> object:
            if self.sort in ("mtime", "size"):
                try:
                    stat = n.path.stat()
                    return -(stat.st_mtime if self.sort == "mtime" else stat.st_size)
                except OSError:
                    return 0
            return "".join(c for c in unicodedata.normalize("NFKD", n.path.name.casefold())
                           if not unicodedata.combining(c))
        children.sort(key=key, reverse=self.sort == "reverse")
        children.sort(key=lambda n: not n.is_dir)
        return children

    def refresh(self) -> None:
        """Refresh expanded nodes, or matching descendants with ancestor context."""
        self.errors = []
        selected = self.current.path if self.visible_nodes else None
        visible = []
        def visit(node: TreeNode, depth: int) -> list[tuple[TreeNode, int]]:
            result = []
            for child in self._children(node):
                descendants = visit(child, depth + 1) if child.is_dir and (
                    child.expanded or self.pattern) and depth < 64 else []
                if self.pattern is None or self.pattern.search(child.path.name) or descendants:
                    result.append((child, depth))
                    result.extend(descendants)
            return result
        visible = visit(self.root, 0)
        self.visible_nodes = visible
        self.cursor_index = next((i for i, (n, _) in enumerate(visible) if n.path == selected),
                                 min(self.cursor_index, max(0, len(visible) - 1)))

    def filter(self, value: str) -> None:
        """Apply a regex filter; invalid regex leaves the old filter intact."""
        compiled = re.compile(value, re.I) if value else None
        self.pattern = compiled
        self.refresh()

    def move(self, delta: int) -> None:
        """Move the selected row."""
        self.cursor_index = max(0, min(self.cursor_index + delta, len(self.visible_nodes) - 1))

    def toggle_expand(self) -> None:
        """Expand/collapse a directory."""
        if self.current.is_dir:
            self.current.expanded = not self.current.expanded
            self.refresh()

    def parent(self) -> None:
        """Move the tree root to its parent."""
        self.root = TreeNode(self.root.path.parent, True, expanded=True)
        self.cursor_index = 0
        self.refresh()

    def create(self, name: str, directory: bool = False) -> Path:
        """Create a direct child; refuse path traversal or overwriting."""
        if not name or name in (".", "..") or Path(name).name != name:
            raise ValueError("Un nom simple est attendu")
        base = self.current.path if self.current.is_dir else self.current.path.parent
        path = base / name
        if directory:
            path.mkdir()
        else:
            with path.open("x", encoding="utf-8"):
                pass
        self.refresh()
        return path

    def rename(self, name: str) -> None:
        """Rename a selected entry, refusing collisions."""
        if not self.visible_nodes:
            return
        if not name or name in (".", "..") or Path(name).name != name:
            raise ValueError("Un nom simple est attendu")
        target = self.current.path.with_name(name)
        if os.path.lexists(target):
            raise FileExistsError(str(target))
        self.current.path.rename(target)
        self.cache.clear()
        self.refresh()

    def delete(self) -> None:
        """Delete a selected file or empty directory (confirmation belongs to UI)."""
        if not self.visible_nodes:
            return
        node = self.current
        node.path.rmdir() if node.is_dir else node.path.unlink()
        self.cache.clear()
        self.refresh()
