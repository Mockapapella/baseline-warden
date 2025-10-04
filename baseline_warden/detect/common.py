"""Shared detection types and helpers."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, List, Optional, Sequence, Set


@dataclass(frozen=True)
class Detection:
    """Represents a single detected BCD key in a source file."""

    path: Path
    line: int
    bcd_key: str
    detail: Optional[str] = None


def _is_ignored(relative_path: Path, ignore_globs: Sequence[str]) -> bool:
    rel = str(relative_path).replace("\\", "/")
    return any(fnmatch.fnmatch(rel, pattern) for pattern in ignore_globs)


def iter_included_files(
    root: Path,
    include_patterns: Sequence[str],
    ignore_patterns: Sequence[str],
    *,
    extensions: Optional[Set[str]] = None,
) -> Iterator[Path]:
    """Yield files under ``root`` that match include patterns and skip ignores."""

    seen: Set[Path] = set()
    ext_set = {ext.lower() for ext in extensions} if extensions else None

    for pattern in include_patterns:
        for path in root.glob(pattern):
            if path.is_dir():
                continue
            if ext_set and path.suffix.lower() not in ext_set:
                continue
            relative = path.relative_to(root)
            if _is_ignored(relative, ignore_patterns):
                continue
            if relative in seen:
                continue
            seen.add(relative)
            yield path


__all__ = ["Detection", "iter_included_files"]
