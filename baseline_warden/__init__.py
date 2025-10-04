"""Baseline Warden package."""

from importlib import metadata


try:
    __version__ = metadata.version("baseline-warden")
except metadata.PackageNotFoundError:  # pragma: no cover - local editable install
    __version__ = "0.0.0"

__all__ = ["__version__"]
