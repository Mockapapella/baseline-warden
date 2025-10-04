"""Configuration models for Baseline Warden."""

from __future__ import annotations

from pathlib import Path
from typing import List, Literal

from pydantic import BaseModel, Field

try:  # Python 3.11+
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover - fallback for <3.11
    import tomli as tomllib  # type: ignore[no-redef]


RequiredStatus = Literal["widely", "newly_or_widely"]
UnknownBehavior = Literal["warn", "fail", "ignore"]


class PolicyConfig(BaseModel):
    required_status: RequiredStatus = Field(
        "newly_or_widely",
        description="Baseline level required for conformance.",
    )
    unknown_behavior: UnknownBehavior = Field(
        "warn",
        description="How to treat tokens that cannot be mapped to Baseline data.",
    )


class IncludeConfig(BaseModel):
    paths: List[str] = Field(
        default_factory=lambda: [
            # Common web project locations (recursive)
            "**/templates/**",
            "**/static/**",
            # Top-level fallbacks
            "templates/**",
            "static/**",
            "src/**",
        ]
    )


class IgnoreConfig(BaseModel):
    globs: List[str] = Field(
        default_factory=lambda: [
            "node_modules/**",
            "dist/**",
            "build/**",
            "vendor/**",
            "coverage/**",
            ".next/**",
            ".vite/**",
            ".output/**",
            "staticfiles/**",
            "**/*.min.*",
        ]
    )


class OutputConfig(BaseModel):
    formats: List[str] = Field(default_factory=lambda: ["console", "json", "gh-annotations"])


class AllowListConfig(BaseModel):
    feature_ids: List[str] = Field(default_factory=list)
    bcd_keys: List[str] = Field(default_factory=list)


class BaselineWardenConfig(BaseModel):
    policy: PolicyConfig = Field(default_factory=PolicyConfig)
    include: IncludeConfig = Field(default_factory=IncludeConfig)
    ignore: IgnoreConfig = Field(default_factory=IgnoreConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    allowlist: AllowListConfig = Field(default_factory=AllowListConfig)


def load_config(path: Path) -> BaselineWardenConfig:
    """Load configuration from a TOML file."""
    data = tomllib.loads(path.read_text())
    return BaselineWardenConfig.model_validate(data)


__all__ = ["BaselineWardenConfig", "load_config"]
