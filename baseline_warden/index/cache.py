"""Lock file helpers for Baseline Warden."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field, computed_field


class LockFeature(BaseModel):
    """Minimal Baseline feature representation stored in the lock file."""

    feature_id: str = Field(description="Unique Baseline feature identifier")
    title: Optional[str] = Field(default=None, description="Human readable feature title")
    status: Optional[str] = Field(default=None, description="Baseline status (widely/newly/limited)")
    low_date: Optional[str] = Field(default=None, description="Baseline low date (ISO 8601)")
    high_date: Optional[str] = Field(default=None, description="Baseline high date (ISO 8601)")
    bcd_keys: List[str] = Field(default_factory=list, description="Associated BCD keys")


class BaselineLock(BaseModel):
    """Top-level lock snapshot structure."""

    version: int = Field(default=1, description="Schema version for the lock file")
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="UTC timestamp describing when the snapshot was generated",
    )
    features: List[LockFeature] = Field(default_factory=list, description="Feature metadata included in the snapshot")

    @computed_field
    @property
    def feature_count(self) -> int:
        """Number of features stored in the lock."""

        return len(self.features)


def load_lock(path: Path) -> BaselineLock:
    """Load a Baseline lock snapshot from disk."""

    data = json.loads(path.read_text(encoding="utf-8"))
    return BaselineLock.model_validate(data)


def write_lock(path: Path, lock: BaselineLock) -> None:
    """Persist a Baseline lock snapshot to disk as JSON."""

    payload = lock.model_dump(mode="json", exclude_none=True)
    payload["feature_count"] = lock.feature_count
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


__all__ = ["BaselineLock", "LockFeature", "load_lock", "write_lock"]
